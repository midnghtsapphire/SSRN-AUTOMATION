#!/usr/bin/env python3
"""
SSRN Paper Generator
Generates academic papers with human voice and proper formatting
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from openai import OpenAI


class SSRNPaperGenerator:
    """Generates SSRN papers with quality controls"""
    
    def __init__(self):
        self.client = OpenAI()
        self.author = "Audrey Evans"
        self.orcid = "0009-0005-0663-7832"
        self.affiliation = "Independent Researcher"
        self.email = "angelreporters@gmail.com"
        
    def identify_sub_niche(self, main_topic):
        """Identify a specific sub-niche within the main topic"""
        prompt = f"""Given this main research topic: "{main_topic}"

Identify ONE specific sub-niche or focused aspect that would make an excellent standalone academic paper.

Requirements:
- Must be a narrower, more specific aspect of the main topic
- Should be substantive enough for a full paper
- Use academic terminology
- Be specific and concrete
- Maximum 8 words

Examples:
- Main: "Climate risk in financial markets" → Sub-niche: "Carbon pricing effects on equity valuations"
- Main: "Cryptocurrency market microstructure" → Sub-niche: "Order flow toxicity in Bitcoin exchanges"
- Main: "ESG investing performance" → Sub-niche: "Green bond premium determinants"

Return ONLY the sub-niche topic, nothing else."""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_contra_title(self, topic):
        """Generate a contra-suggestive title (opposing concepts)"""
        prompt = f"""Generate a compelling academic paper title about {topic} that uses contra-suggestive phrasing (opposing concepts).

Examples of contra-suggestive titles:
- "Rational Irrationality: How Quantum Cognition Challenges Classical Investor Biases"
- "Efficient Inefficiency: Market Microstructure and Price Discovery Paradoxes"
- "Predictable Unpredictability: Chaos Theory in Financial Time Series"

Requirements:
- Use opposing or paradoxical concepts
- Sound academic and professional
- Be specific to {topic}
- Maximum 15 words
- Do NOT include any AI-related terms

Return ONLY the title, nothing else."""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_subtitle(self, title, topic):
        """Generate an engaging subtitle"""
        prompt = f"""Given this paper title: "{title}"

Generate a compelling subtitle that:
- Expands on the main title
- Sounds natural and human-written
- Is specific and informative
- Maximum 12 words
- Uses active, engaging language

Return ONLY the subtitle, nothing else."""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_keywords(self, title, topic):
        """Generate SEO-optimized keywords"""
        prompt = f"""Generate 5-7 SEO-optimized keywords for this academic paper:

Title: {title}
Topic: {topic}

Requirements:
- Relevant to finance, economics, or business research
- Mix of broad and specific terms
- Natural academic terminology
- Comma-separated list
- No AI-related terms

Return ONLY the keywords as a comma-separated list."""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_jel_codes(self, title, topic):
        """Generate appropriate JEL classification codes"""
        prompt = f"""Generate 3-4 appropriate JEL classification codes for this paper:

Title: {title}
Topic: {topic}

Return ONLY the JEL codes as a comma-separated list (e.g., D83, G11, C91, D81)."""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_abstract(self, title, subtitle, topic):
        """Generate a concise abstract (≤200 words)"""
        prompt = f"""Write a professional academic abstract for this paper:

Title: {title}
Subtitle: {subtitle}
Topic: {topic}

Requirements:
- Maximum 200 words
- Written in authentic human academic voice
- Clear research question and findings
- No AI-related terms or phrases
- No mentions of "this paper was generated" or similar
- Sound like a real researcher wrote it
- Use active voice where appropriate
- Be specific and substantive

Write the abstract now:"""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        
        abstract = response.choices[0].message.content.strip()
        
        # Ensure it's under 200 words
        words = abstract.split()
        if len(words) > 200:
            abstract = ' '.join(words[:200]) + '.'
        
        return abstract
    
    def generate_section(self, title, subtitle, topic, section_name, section_description):
        """Generate a paper section with human voice"""
        prompt = f"""You are writing a section for an academic paper. Write in the authentic voice of an experienced researcher.

Paper Title: {title}
Subtitle: {subtitle}
Topic: {topic}

Section: {section_name}
Purpose: {section_description}

CRITICAL REQUIREMENTS:
- Write as if you ARE the researcher (Audrey Evans), not as an AI
- Use natural academic language that a human would write
- NO AI-style phrases like "it's important to note", "it is worth noting"
- NO mentions of AI, automation, or generation
- NO author name in the body text
- Use specific examples and substantive analysis
- Write 3-4 paragraphs (600-800 words)
- Double-spaced formatting will be applied later
- Sound confident and authoritative

Write the {section_name} section now:"""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200
        )
        
        return response.choices[0].message.content.strip()
    
    def clean_ai_artifacts(self, text):
        """Remove any AI-related artifacts from the text"""
        # Remove common AI phrases
        ai_phrases = [
            r'as an ai[^.]*\.',
            r'i cannot[^.]*\.',
            r'i don\'t have[^.]*\.',
            r'as a language model[^.]*\.',
            r'it\'s important to note that',
            r'it is worth noting that',
            r'this (?:paper|study|research) was generated',
            r'(?:manus|ai|automated|auto-generated)',
        ]
        
        for phrase in ai_phrases:
            text = re.sub(phrase, '', text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def generate_full_paper(self, topic, paper_type="main", main_topic=None):
        """Generate a complete academic paper"""
        paper_label = "MAIN PAPER" if paper_type == "main" else "SUB-NICHE PAPER"
        print(f"\n{'='*60}")
        print(f"SSRN Paper Generation - {paper_label}")
        print(f"{'='*60}\n")
        if main_topic and paper_type == "sub-niche":
            print(f"Main Topic: {main_topic}")
        print(f"Topic: {topic}\n")
        
        # Generate metadata
        print("→ Generating title...")
        title = self.generate_contra_title(topic)
        print(f"  Title: {title}\n")
        
        print("→ Generating subtitle...")
        subtitle = self.generate_subtitle(title, topic)
        print(f"  Subtitle: {subtitle}\n")
        
        print("→ Generating keywords...")
        keywords = self.generate_keywords(title, topic)
        print(f"  Keywords: {keywords}\n")
        
        print("→ Generating JEL codes...")
        jel_codes = self.generate_jel_codes(title, topic)
        print(f"  JEL Codes: {jel_codes}\n")
        
        print("→ Generating abstract...")
        abstract = self.generate_abstract(title, subtitle, topic)
        print(f"  Abstract: {len(abstract.split())} words\n")
        
        # Generate paper sections
        sections = {
            "Introduction": "Introduce the research question, motivation, and contribution",
            "Methodology": "Describe the research approach, data sources, and analytical framework",
            "Analysis": "Present the main findings and empirical results",
            "Discussion": "Interpret the results and discuss implications",
            "Conclusion": "Summarize findings and suggest future research directions"
        }
        
        body_html = ""
        for section_name, section_desc in sections.items():
            print(f"→ Generating {section_name}...")
            section_text = self.generate_section(title, subtitle, topic, section_name, section_desc)
            section_text = self.clean_ai_artifacts(section_text)
            
            # Convert to HTML
            body_html += f"<h3>{section_name}</h3>\n"
            paragraphs = section_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    body_html += f"<p>{para.strip()}</p>\n"
        
        # Compile paper data
        paper_data = {
            "title": title,
            "subtitle": subtitle,
            "author": self.author,
            "orcid": self.orcid,
            "affiliation": self.affiliation,
            "email": self.email,
            "date": datetime.now().strftime("%B %d, %Y"),
            "date_short": datetime.now().strftime("%Y%m%d"),
            "keywords": keywords,
            "jel_codes": jel_codes,
            "abstract": abstract,
            "body": body_html,
            "topic": topic
        }
        
        # Add paper type to metadata
        paper_data["paper_type"] = paper_type
        if main_topic and paper_type == "sub-niche":
            paper_data["main_topic"] = main_topic
        
        print(f"\n✅ {paper_label} generation complete!\n")
        
        return paper_data


    def generate_main_and_subniche(self, main_topic):
        """Generate both main paper and sub-niche paper"""
        print(f"\n{'#'*60}")
        print("DUAL PAPER GENERATION")
        print(f"{'#'*60}")
        print(f"Main Topic: {main_topic}\n")
        
        # Identify sub-niche
        print("→ Identifying sub-niche topic...")
        sub_niche_topic = self.identify_sub_niche(main_topic)
        print(f"  Sub-niche: {sub_niche_topic}\n")
        
        # Generate main paper
        print("\n[1/2] Generating MAIN paper...\n")
        main_paper = self.generate_full_paper(main_topic, paper_type="main")
        
        # Generate sub-niche paper
        print("\n[2/2] Generating SUB-NICHE paper...\n")
        sub_niche_paper = self.generate_full_paper(sub_niche_topic, paper_type="sub-niche", main_topic=main_topic)
        
        return {
            "main_paper": main_paper,
            "sub_niche_paper": sub_niche_paper,
            "main_topic": main_topic,
            "sub_niche_topic": sub_niche_topic
        }


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_paper.py <topic> [--dual]")
        sys.exit(1)
    
    # Check for dual mode flag
    dual_mode = '--dual' in sys.argv
    if dual_mode:
        sys.argv.remove('--dual')
    
    topic = ' '.join(sys.argv[1:])
    
    generator = SSRNPaperGenerator()
    
    if dual_mode:
        # Generate both main and sub-niche papers
        result = generator.generate_main_and_subniche(topic)
        
        # Save both papers
        output_dir = Path(__file__).parent.parent / 'output'
        output_dir.mkdir(exist_ok=True)
        
        date_str = result['main_paper']['date_short']
        
        # Save main paper
        main_file = output_dir / f"paper_data_main_{date_str}.json"
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(result['main_paper'], f, indent=2, ensure_ascii=False)
        print(f"\n✅ Main paper saved: {main_file}")
        
        # Save sub-niche paper
        sub_file = output_dir / f"paper_data_subniche_{date_str}.json"
        with open(sub_file, 'w', encoding='utf-8') as f:
            json.dump(result['sub_niche_paper'], f, indent=2, ensure_ascii=False)
        print(f"✅ Sub-niche paper saved: {sub_file}")
        
        # Save combined metadata
        meta_file = output_dir / f"dual_papers_meta_{date_str}.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump({
                "main_topic": result['main_topic'],
                "sub_niche_topic": result['sub_niche_topic'],
                "main_paper_file": str(main_file),
                "sub_niche_paper_file": str(sub_file),
                "date": date_str
            }, f, indent=2, ensure_ascii=False)
        print(f"✅ Metadata saved: {meta_file}\n")
        
    else:
        # Generate single paper (legacy mode)
        paper_data = generator.generate_full_paper(topic)
        
        # Save paper data as JSON
        output_dir = Path(__file__).parent.parent / 'output'
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"paper_data_{paper_data['date_short']}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(paper_data, f, indent=2, ensure_ascii=False)
        
        print(f"Paper data saved to: {output_file}")


if __name__ == '__main__':
    main()
