#!/usr/bin/env python3
"""
SSRN Paper Automation - Main Orchestrator
Complete workflow from generation to upload
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime


class SSRNAutomation:
    """Main automation orchestrator"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.scripts_dir = self.base_dir / 'scripts'
        self.output_dir = self.base_dir / 'output'
        self.metadata_dir = self.base_dir / 'metadata'
        self.logs_dir = self.base_dir / 'logs'
        
        # Ensure directories exist
        for dir_path in [self.output_dir, self.metadata_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def log(self, message):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # Append to log file
        log_file = self.logs_dir / f"automation_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def run_script(self, script_name, args=None):
        """Run a Python script and return result"""
        script_path = self.scripts_dir / script_name
        cmd = ['python3', str(script_path)]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result
    
    def generate_papers(self, topic):
        """Step 1: Generate both main and sub-niche papers"""
        self.log(f"{'='*60}")
        self.log("STEP 1: Generating Papers (Main + Sub-Niche)")
        self.log(f"{'='*60}")
        self.log(f"Topic: {topic}")
        
        # Generate with --dual flag
        result = self.run_script('generate_paper.py', [topic, '--dual'])
        
        if result.returncode != 0:
            self.log(f"❌ Paper generation failed: {result.stderr}")
            return None, None
        
        # Find the generated JSON files
        date_str = datetime.now().strftime('%Y%m%d')
        main_json = self.output_dir / f"paper_data_main_{date_str}.json"
        sub_json = self.output_dir / f"paper_data_subniche_{date_str}.json"
        
        if not main_json.exists() or not sub_json.exists():
            self.log(f"❌ Paper data files not found")
            return None, None
        
        self.log(f"✅ Main paper generated: {main_json}")
        self.log(f"✅ Sub-niche paper generated: {sub_json}")
        return main_json, sub_json
    
    def create_pdf(self, json_file, paper_type="main"):
        """Step 2: Create PDF from paper data"""
        self.log(f"\n{'='*60}")
        self.log("STEP 2: Creating PDF")
        self.log(f"{'='*60}")
        
        # Load paper data
        with open(json_file, 'r', encoding='utf-8') as f:
            paper_data = json.load(f)
        
        # Load HTML template
        template_path = self.scripts_dir / 'paper_template.html'
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Fill template
        html_content = template
        for key, value in paper_data.items():
            placeholder = f"{{{{{key}}}}}"
            html_content = html_content.replace(placeholder, str(value))
        
        # Save HTML
        type_suffix = f"_{paper_type}" if paper_type != "main" else ""
        html_file = self.output_dir / f"paper{type_suffix}_{paper_data['date_short']}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.log(f"✅ HTML created ({paper_type}): {html_file}")
        
        # Convert to PDF using weasyprint
        # Create short title for filename
        short_title = self._create_short_title(paper_data['title'])
        pdf_filename = f"Walter_Evans_{short_title}_{paper_data['date_short']}.pdf"
        pdf_file = self.output_dir / pdf_filename
        
        self.log(f"→ Converting to PDF: {pdf_filename}")
        
        try:
            from weasyprint import HTML
            HTML(filename=str(html_file)).write_pdf(str(pdf_file))
            self.log(f"✅ PDF created: {pdf_file}")
            return pdf_file
        except Exception as e:
            self.log(f"❌ PDF conversion failed: {e}")
            return None
    
    def _create_short_title(self, title):
        """Create short title for filename"""
        words = title.split(':')[0].split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        meaningful_words = [w for w in words if w.lower() not in stop_words]
        short_words = meaningful_words[:3] if len(meaningful_words) >= 3 else meaningful_words[:2]
        short_title = '_'.join(short_words)
        short_title = ''.join(c for c in short_title if c.isalnum() or c == '_')
        return short_title
    
    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF for quality checking"""
        result = subprocess.run(
            ['pdftotext', str(pdf_file), '-'],
            capture_output=True,
            text=True
        )
        return result.stdout
    
    def quality_check(self, pdf_file):
        """Step 3: Run quality checks"""
        self.log(f"\n{'='*60}")
        self.log("STEP 3: Quality Check")
        self.log(f"{'='*60}")
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_file)
        
        # Save text to temp file
        text_file = self.output_dir / f"temp_text_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Run quality checker
        result = self.run_script('quality_checker.py', [str(pdf_file), str(text_file)])
        
        # Clean up temp file
        text_file.unlink()
        
        if result.returncode != 0:
            self.log(f"⚠️  Quality check found issues")
            self.log(result.stdout)
            return False
        
        self.log(f"✅ Quality check passed")
        return True
    
    def extract_metadata(self, json_file):
        """Step 4: Extract and save metadata"""
        self.log(f"\n{'='*60}")
        self.log("STEP 4: Extracting Metadata")
        self.log(f"{'='*60}")
        
        result = self.run_script('extract_metadata.py', [str(json_file)])
        
        if result.returncode != 0:
            self.log(f"❌ Metadata extraction failed: {result.stderr}")
            return None
        
        # Find metadata file
        with open(json_file, 'r', encoding='utf-8') as f:
            paper_data = json.load(f)
        
        metadata_file = self.metadata_dir / f"metadata_{paper_data['date_short']}.json"
        
        if metadata_file.exists():
            self.log(f"✅ Metadata extracted: {metadata_file}")
            return metadata_file
        
        return None
    
    def upload_to_gdrive(self, pdf_file, metadata_file):
        """Step 5: Upload to Google Drive"""
        self.log(f"\n{'='*60}")
        self.log("STEP 5: Upload to Google Drive")
        self.log(f"{'='*60}")
        
        result = self.run_script('upload_and_backup.py', [str(pdf_file), str(metadata_file)])
        
        if result.returncode != 0:
            self.log(f"⚠️  Upload had issues: {result.stderr}")
            return None
        
        # Extract Google Drive link from output
        gdrive_link = None
        for line in result.stdout.split('\n'):
            if 'drive.google.com' in line:
                gdrive_link = line.strip().split()[-1]
                break
        
        self.log(f"✅ Upload complete")
        return gdrive_link
    
    def send_notifications(self, metadata_file, gdrive_link):
        """Step 6: Send email and calendar notifications"""
        self.log(f"\n{'='*60}")
        self.log("STEP 6: Sending Notifications")
        self.log(f"{'='*60}")
        
        result = self.run_script('send_notifications.py', [str(metadata_file), gdrive_link or 'N/A'])
        
        if result.returncode != 0:
            self.log(f"⚠️  Notifications had issues: {result.stderr}")
            return False
        
        self.log(f"✅ Notifications sent")
        return True
    
    def run_full_workflow(self, topic):
        """Run complete automation workflow for BOTH main and sub-niche papers"""
        start_time = datetime.now()
        
        self.log(f"\n{'#'*60}")
        self.log("SSRN DUAL PAPER AUTOMATION - FULL WORKFLOW")
        self.log(f"{'#'*60}")
        self.log(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"Topic: {topic}")
        self.log(f"{'#'*60}\n")
        
        try:
            # Step 1: Generate BOTH papers (main + sub-niche)
            main_json, sub_json = self.generate_papers(topic)
            if not main_json or not sub_json:
                raise Exception("Paper generation failed")
            
            # Step 2: Create PDFs for BOTH papers
            self.log(f"\n{'='*60}")
            self.log("STEP 2: Creating PDFs (Main + Sub-Niche)")
            self.log(f"{'='*60}")
            
            main_pdf = self.create_pdf(main_json, paper_type="main")
            if not main_pdf:
                raise Exception("Main PDF creation failed")
            
            sub_pdf = self.create_pdf(sub_json, paper_type="subniche")
            if not sub_pdf:
                raise Exception("Sub-niche PDF creation failed")
            
            # Step 3: Quality check BOTH papers
            self.log(f"\n{'='*60}")
            self.log("STEP 3: Quality Check (Main + Sub-Niche)")
            self.log(f"{'='*60}")
            
            self.log("\n→ Checking MAIN paper...")
            if not self.quality_check(main_pdf):
                self.log("⚠️  Main paper quality check found issues, but continuing...")
            
            self.log("\n→ Checking SUB-NICHE paper...")
            if not self.quality_check(sub_pdf):
                self.log("⚠️  Sub-niche paper quality check found issues, but continuing...")
            
            # Step 4: Extract metadata for BOTH papers
            self.log(f"\n{'='*60}")
            self.log("STEP 4: Extracting Metadata (Main + Sub-Niche)")
            self.log(f"{'='*60}")
            
            main_metadata = self.extract_metadata(main_json)
            sub_metadata = self.extract_metadata(sub_json)
            
            if not main_metadata or not sub_metadata:
                raise Exception("Metadata extraction failed")
            
            # Step 5: Upload BOTH papers to Google Drive
            self.log(f"\n{'='*60}")
            self.log("STEP 5: Upload to Google Drive (Main + Sub-Niche)")
            self.log(f"{'='*60}")
            
            main_gdrive_link = self.upload_to_gdrive(main_pdf, main_metadata)
            sub_gdrive_link = self.upload_to_gdrive(sub_pdf, sub_metadata)
            
            if not main_gdrive_link:
                self.log("⚠️  Main paper upload had issues")
            if not sub_gdrive_link:
                self.log("⚠️  Sub-niche paper upload had issues")
            
            # Step 6: Send notifications for BOTH papers
            self.log(f"\n{'='*60}")
            self.log("STEP 6: Sending Notifications (Main + Sub-Niche)")
            self.log(f"{'='*60}")
            
            self.log("\n→ Notifying for MAIN paper...")
            if not self.send_notifications(main_metadata, main_gdrive_link):
                self.log("⚠️  Main paper notifications had issues")
            
            self.log("\n→ Notifying for SUB-NICHE paper...")
            if not self.send_notifications(sub_metadata, sub_gdrive_link):
                self.log("⚠️  Sub-niche paper notifications had issues")
            
            # Success!
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.log(f"\n{'#'*60}")
            self.log("✅ DUAL PAPER AUTOMATION COMPLETE!")
            self.log(f"{'#'*60}")
            self.log(f"Duration: {duration:.1f} seconds")
            self.log(f"Main Paper: {main_pdf.name}")
            self.log(f"Sub-Niche Paper: {sub_pdf.name}")
            self.log(f"{'#'*60}\n")
            
            return True
            
        except Exception as e:
            self.log(f"\n{'#'*60}")
            self.log(f"❌ AUTOMATION FAILED: {e}")
            self.log(f"{'#'*60}\n")
            return False


def main():
    if len(sys.argv) < 2:
        print("\nSSRN Paper Automation")
        print("=" * 60)
        print("\nUsage: python run_automation.py <topic>")
        print("\nExample:")
        print("  python run_automation.py 'quantum cognition in behavioral finance'")
        print()
        sys.exit(1)
    
    topic = ' '.join(sys.argv[1:])
    
    automation = SSRNAutomation()
    success = automation.run_full_workflow(topic)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
