#!/usr/bin/env python3
"""
SSRN Metadata Extractor
Extracts metadata from papers and generates CSV for tracking
"""

import json
import csv
from pathlib import Path
from datetime import datetime


class MetadataExtractor:
    """Extracts and manages paper metadata"""
    
    def __init__(self, metadata_dir):
        self.metadata_dir = Path(metadata_dir)
        self.metadata_dir.mkdir(exist_ok=True)
        
    def extract_from_json(self, json_path):
        """Extract metadata from paper JSON data"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create short title for filename (remove special chars, limit length)
        short_title = self._create_short_title(data['title'])
        
        metadata = {
            'filename': f"Walter_Evans_{short_title}_{data['date_short']}.pdf",
            'title': data['title'],
            'subtitle': data['subtitle'],
            'author': data['author'],
            'orcid': data['orcid'],
            'email': data['email'],
            'date': data['date'],
            'date_short': data['date_short'],
            'abstract': data['abstract'],
            'keywords': data['keywords'],
            'jel_codes': data['jel_codes'],
            'topic': data['topic'],
            'word_count': self._estimate_word_count(data['body']),
            'ejournals': self._suggest_ejournals(data['keywords'], data['jel_codes'])
        }
        
        return metadata
    
    def _create_short_title(self, title):
        """Create a short title for filename"""
        # Take first meaningful words, remove special characters
        words = title.split(':')[0].split()
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        meaningful_words = [w for w in words if w.lower() not in stop_words]
        
        # Take first 2-3 meaningful words
        short_words = meaningful_words[:3] if len(meaningful_words) >= 3 else meaningful_words[:2]
        
        # Join and clean
        short_title = '_'.join(short_words)
        short_title = ''.join(c for c in short_title if c.isalnum() or c == '_')
        
        return short_title
    
    def _estimate_word_count(self, html_body):
        """Estimate word count from HTML body"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_body)
        return len(text.split())
    
    def _suggest_ejournals(self, keywords, jel_codes):
        """Suggest appropriate eJournals based on keywords and JEL codes"""
        # Map JEL codes to eJournals
        jel_mapping = {
            'D': ['Behavioral & Experimental Economics', 'Microeconomics'],
            'G': ['Financial Economics', 'Corporate Finance', 'Asset Pricing'],
            'C': ['Econometrics', 'Statistical Methods'],
            'E': ['Macroeconomics', 'Monetary Economics'],
            'L': ['Industrial Organization', 'Business Economics'],
            'M': ['Management', 'Marketing', 'Accounting']
        }
        
        suggested = set()
        
        # Extract first letter of each JEL code
        for code in jel_codes.split(','):
            code = code.strip()
            if code:
                first_letter = code[0].upper()
                if first_letter in jel_mapping:
                    suggested.update(jel_mapping[first_letter])
        
        # Add based on keywords
        keywords_lower = keywords.lower()
        if 'behavioral' in keywords_lower or 'psychology' in keywords_lower:
            suggested.add('Behavioral & Experimental Economics')
        if 'market' in keywords_lower or 'trading' in keywords_lower:
            suggested.add('Financial Markets')
        if 'investment' in keywords_lower or 'portfolio' in keywords_lower:
            suggested.add('Asset Pricing')
        
        return ', '.join(sorted(suggested)[:3])  # Return top 3
    
    def save_metadata(self, metadata):
        """Save metadata to JSON file"""
        output_file = self.metadata_dir / f"metadata_{metadata['date_short']}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Metadata saved: {output_file}")
        return output_file
    
    def update_csv_log(self, metadata):
        """Update CSV log with paper metadata"""
        csv_file = self.metadata_dir / 'papers_log.csv'
        
        # Check if file exists
        file_exists = csv_file.exists()
        
        # Define CSV columns
        fieldnames = [
            'filename', 'title', 'subtitle', 'author', 'orcid', 'email',
            'date', 'date_short', 'keywords', 'jel_codes', 'topic',
            'word_count', 'ejournals', 'abstract'
        ]
        
        # Write to CSV
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write header if new file
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(metadata)
        
        print(f"✅ CSV log updated: {csv_file}")
        return csv_file
    
    def generate_submission_info(self, metadata):
        """Generate submission information file"""
        info_file = self.metadata_dir / f"submission_info_{metadata['date_short']}.txt"
        
        content = f"""SSRN SUBMISSION INFORMATION
{'='*60}

PAPER DETAILS
Filename: {metadata['filename']}
Title: {metadata['title']}
Subtitle: {metadata['subtitle']}

AUTHOR INFORMATION
Name: {metadata['author']}
ORCID: {metadata['orcid']}
Email: {metadata['email']}
Affiliation: Independent Researcher

METADATA
Date: {metadata['date']}
Keywords: {metadata['keywords']}
JEL Codes: {metadata['jel_codes']}
Word Count: {metadata['word_count']}

ABSTRACT
{metadata['abstract']}

SUGGESTED EJOURNALS
{metadata['ejournals']}

SUBMISSION CHECKLIST
□ Review paper for accuracy
□ Verify all metadata is correct
□ Check filename follows Walter_Evans_[ShortTitle]_[YYYYMMDD].pdf
□ Upload to SSRN
□ Submit to suggested eJournals
□ Update tracking spreadsheet

{'='*60}
"""
        
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Submission info generated: {info_file}")
        return info_file


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_metadata.py <paper_json_path>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    metadata_dir = Path(__file__).parent.parent / 'metadata'
    
    extractor = MetadataExtractor(metadata_dir)
    
    print(f"\n{'='*60}")
    print("SSRN Metadata Extraction")
    print(f"{'='*60}\n")
    
    metadata = extractor.extract_from_json(json_path)
    
    print(f"Paper: {metadata['filename']}")
    print(f"Title: {metadata['title']}")
    print(f"Keywords: {metadata['keywords']}")
    print(f"JEL Codes: {metadata['jel_codes']}\n")
    
    extractor.save_metadata(metadata)
    extractor.update_csv_log(metadata)
    extractor.generate_submission_info(metadata)
    
    print(f"\n{'='*60}")
    print("✅ Metadata extraction complete!")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
