import os
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class DiskAnalyzer:
    """Analyze disk usage and produce helpful statistics and recommendations."""

    def __init__(self):
        # Cache file used to store previous analysis results
        self.cache_file = "cache/disk_analysis.json"

    def analyze_folder(self, folder_path):
        """Walk `folder_path` and collect statistics about files and folders.

        Returns a dictionary containing size totals, counts by extension,
        age buckets, size buckets, and lists of largest/oldest files.
        """
        stats = {
            'total_size': 0,
            'file_count': 0,
            'folder_count': 0,
            'by_extension': defaultdict(int),
            'by_age': {'<1d': 0, '1d-7d': 0, '1w-1m': 0, '1m-6m': 0, '6m-1y': 0, '>1y': 0},
            'by_size': {'<1MB': 0, '1MB-10MB': 0, '10MB-100MB': 0, '>100MB': 0},
            'largest_files': [],
            'oldest_files': [],
            'duplicates': []
        }

        # Walk the directory tree
        for root, dirs, files in os.walk(folder_path):
            stats['folder_count'] += len(dirs)

            for file in files:
                try:
                    filepath = os.path.join(root, file)
                    stat = os.stat(filepath)

                    # File size bookkeeping
                    size = stat.st_size
                    stats['total_size'] += size
                    stats['file_count'] += 1

                    # Aggregate size by file extension
                    ext = os.path.splitext(file)[1].lower()
                    if ext:
                        stats['by_extension'][ext] += size

                    # Age buckets measured in days since modification
                    file_age = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
                    if file_age < 1:
                        stats['by_age']['<1d'] += size
                    elif file_age < 7:
                        stats['by_age']['1d-7d'] += size
                    elif file_age < 30:
                        stats['by_age']['1w-1m'] += size
                    elif file_age < 180:
                        stats['by_age']['1m-6m'] += size
                    elif file_age < 365:
                        stats['by_age']['6m-1y'] += size
                    else:
                        stats['by_age']['>1y'] += size

                    # Count files into size categories by bytes
                    if size < 1024 * 1024:
                        stats['by_size']['<1MB'] += 1
                    elif size < 10 * 1024 * 1024:
                        stats['by_size']['1MB-10MB'] += 1
                    elif size < 100 * 1024 * 1024:
                        stats['by_size']['10MB-100MB'] += 1
                    else:
                        stats['by_size']['>100MB'] += 1

                    # Record candidate entries for largest/oldest lists
                    file_info = {
                        'path': filepath,
                        'name': file,
                        'size': size,
                        'modified': datetime.fromtimestamp(stat.st_mtime)
                    }

                    stats['largest_files'].append(file_info)
                    stats['oldest_files'].append(file_info)

                except Exception:
                    # Skip files we cannot stat or access
                    continue

        # Sort largest_files by size (descending) and keep top 10
        stats['largest_files'].sort(key=lambda x: x['size'], reverse=True)
        stats['largest_files'] = stats['largest_files'][:10]

        # Sort oldest_files by modification time (oldest first) and keep top 10
        stats['oldest_files'].sort(key=lambda x: x['modified'])
        stats['oldest_files'] = stats['oldest_files'][:10]

        return stats

    def get_recommendations(self, stats):
        """Generate cleanup recommendations from analysis statistics."""
        recommendations = []

        # Recommend cleaning temporary files if they occupy a lot of space
        if '.tmp' in stats['by_extension']:
            tmp_size = stats['by_extension']['.tmp'] / (1024 * 1024)  # convert to MB
            if tmp_size > 100:
                recommendations.append({
                    'type': 'temporary',
                    'description': f'Large temporary files found ({tmp_size:.1f}MB)',
                    'potential_savings': tmp_size,
                    'priority': 'high'
                })

        # Recommend addressing very old files if they take significant space
        old_files_size = stats['by_age']['>1y'] / (1024 * 1024)
        if old_files_size > 500:
            recommendations.append({
                'type': 'old_files',
                'description': f'Large amount of old files ({old_files_size:.1f}MB older than 1 year)',
                'potential_savings': old_files_size * 0.5,  # rough estimate
                'priority': 'medium'
            })

        # Recommend deduplication if duplicates information is present
        if stats.get('duplicates'):
            duplicate_size = sum(f['size'] for f in stats['duplicates']) / (1024 * 1024)
            if duplicate_size > 100:
                recommendations.append({
                    'type': 'duplicates',
                    'description': f'Duplicate files found ({duplicate_size:.1f}MB potentially recoverable)',
                    'potential_savings': duplicate_size,
                    'priority': 'medium'
                })

        return recommendations

    def save_analysis(self, folder_path, stats):
        """Cache analysis results for `folder_path` to a JSON file."""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

        cache_data = {}
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)

        cache_data[folder_path] = {
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }

        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)

    def load_analysis(self, folder_path):
        """Load cached analysis for a folder if available."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
                return cache_data.get(folder_path)
        return None