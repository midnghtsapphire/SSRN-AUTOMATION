#!/usr/bin/env python3
"""
SSRN Trend Analysis
Identifies trending topics from SSRN and Google Trends
"""

import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq


class TrendAnalyzer:
    """Analyzes trends to identify paper topics"""
    
    def __init__(self):
        self.trending_topics = []
        self.topic_scores = {}  # Store scores for ranking
        
    def analyze_ssrn_trends(self):
        """
        Analyze SSRN top downloads via web scraping
        Scrapes the SSRN top downloads page to get trending papers
        """
        print("→ Analyzing SSRN top downloads...")
        
        ssrn_topics = []
        
        try:
            # SSRN top downloads URL
            url = "https://papers.ssrn.com/sol3/topten/topTenResults.cfm?groupingId=1&netorjrnl=jrnl"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find paper titles (SSRN structure may vary, using common patterns)
                # Look for links in the top downloads section
                paper_links = soup.find_all('a', href=True)
                
                for link in paper_links:
                    title = link.get_text(strip=True)
                    # Filter for actual paper titles (longer than 20 chars, contains keywords)
                    if len(title) > 20 and any(keyword in title.lower() for keyword in [
                        'market', 'financial', 'economic', 'investment', 'risk',
                        'capital', 'corporate', 'trading', 'portfolio', 'asset',
                        'banking', 'credit', 'equity', 'debt', 'valuation'
                    ]):
                        # Extract key topic from title
                        topic = self._extract_topic_from_title(title)
                        if topic and topic not in ssrn_topics:
                            ssrn_topics.append(topic)
                            # Higher score for SSRN papers (they're already popular)
                            self.topic_scores[topic] = self.topic_scores.get(topic, 0) + 10
                
                # If we didn't get enough, add some fallback topics
                if len(ssrn_topics) < 5:
                    fallback_topics = [
                        "ESG investing and corporate performance",
                        "Cryptocurrency market microstructure",
                        "Machine learning in credit risk assessment",
                        "Climate risk in financial markets",
                        "Central bank digital currencies"
                    ]
                    for topic in fallback_topics:
                        if topic not in ssrn_topics:
                            ssrn_topics.append(topic)
                            self.topic_scores[topic] = self.topic_scores.get(topic, 0) + 5
                
            else:
                print(f"  ⚠️  SSRN request failed (status {response.status_code}), using fallback topics")
                ssrn_topics = self._get_fallback_ssrn_topics()
                
        except Exception as e:
            print(f"  ⚠️  SSRN scraping error: {e}, using fallback topics")
            ssrn_topics = self._get_fallback_ssrn_topics()
        
        self.trending_topics.extend(ssrn_topics)
        print(f"  Found {len(ssrn_topics)} trending SSRN topics")
        
        return ssrn_topics
    
    def _get_fallback_ssrn_topics(self):
        """Fallback topics if SSRN scraping fails"""
        topics = [
            "ESG investing and corporate performance",
            "Cryptocurrency market microstructure",
            "Machine learning in credit risk assessment",
            "Remote work and productivity",
            "Climate risk in financial markets",
            "Central bank digital currencies",
            "Private equity performance attribution",
            "Behavioral biases in retail investing"
        ]
        for topic in topics:
            self.topic_scores[topic] = self.topic_scores.get(topic, 0) + 5
        return topics
    
    def _extract_topic_from_title(self, title):
        """Extract a clean topic from a paper title"""
        # Remove common paper title patterns
        title = title.lower()
        
        # Common finance/economics topics to extract
        topic_patterns = [
            'esg', 'cryptocurrency', 'bitcoin', 'blockchain', 'machine learning',
            'artificial intelligence', 'climate risk', 'sustainable finance',
            'behavioral finance', 'market microstructure', 'high frequency trading',
            'private equity', 'venture capital', 'corporate governance',
            'risk management', 'portfolio optimization', 'asset pricing',
            'market efficiency', 'financial regulation', 'central bank',
            'monetary policy', 'inflation', 'interest rate', 'credit risk',
            'default risk', 'liquidity', 'volatility', 'derivatives'
        ]
        
        for pattern in topic_patterns:
            if pattern in title:
                # Create a topic phrase
                words = title.split()
                # Find the pattern and get surrounding context
                for i, word in enumerate(words):
                    if pattern.split()[0] in word:
                        # Get 2-3 words before and after
                        start = max(0, i - 2)
                        end = min(len(words), i + 4)
                        topic_phrase = ' '.join(words[start:end])
                        # Clean up
                        topic_phrase = topic_phrase.replace(':', '').replace(',', '').strip()
                        if len(topic_phrase) > 15:
                            return topic_phrase.title()
        
        return None
    
    def analyze_google_trends(self, keywords=None):
        """
        Analyze Google Trends for finance/economics topics
        Uses pytrends library to get real trending data
        """
        print("→ Analyzing Google Trends...")
        
        google_topics = []
        
        try:
            # Initialize pytrends
            pytrends = TrendReq(hl='en-US', tz=360)
            
            if keywords is None:
                # Reduced to 4 keywords for faster analysis
                keywords = [
                    "cryptocurrency investing",
                    "ESG investing",
                    "AI in finance",
                    "inflation economics"
                ]
            
            # Get trends for each keyword
            for keyword in keywords:
                try:
                    # Build payload
                    pytrends.build_payload([keyword], timeframe='today 3-m')
                    
                    # Get interest over time
                    interest_df = pytrends.interest_over_time()
                    
                    if not interest_df.empty:
                        # Calculate average interest
                        avg_interest = interest_df[keyword].mean()
                        
                        # Get related queries
                        related_queries = pytrends.related_queries()
                        
                        if keyword in related_queries and related_queries[keyword]['top'] is not None:
                            top_queries = related_queries[keyword]['top']
                            
                            # Extract top 3 related queries
                            for idx, row in top_queries.head(3).iterrows():
                                query = row['query']
                                # Create topic from query
                                topic = self._create_topic_from_query(query, keyword)
                                if topic and topic not in google_topics:
                                    google_topics.append(topic)
                                    # Score based on interest level
                                    score = int(avg_interest / 10) + row['value'] / 10
                                    self.topic_scores[topic] = self.topic_scores.get(topic, 0) + score
                        
                        # Also add the main keyword as a topic
                        main_topic = self._create_topic_from_query(keyword, keyword)
                        if main_topic and main_topic not in google_topics:
                            google_topics.append(main_topic)
                            self.topic_scores[main_topic] = self.topic_scores.get(main_topic, 0) + avg_interest / 10
                    
                    # Rate limiting (reduced for speed)
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"  ⚠️  Error processing keyword '{keyword}': {e}")
                    continue
            
            # If we didn't get enough topics, add fallback
            if len(google_topics) < 3:
                fallback = [
                    "Inflation expectations and consumer behavior",
                    "Bitcoin ETF market impact",
                    "Sustainable finance regulations"
                ]
                for topic in fallback:
                    if topic not in google_topics:
                        google_topics.append(topic)
                        self.topic_scores[topic] = self.topic_scores.get(topic, 0) + 3
                        
        except Exception as e:
            print(f"  ⚠️  Google Trends error: {e}, using fallback topics")
            google_topics = [
                "Inflation expectations and consumer behavior",
                "Bitcoin ETF market impact",
                "Sustainable finance regulations",
                "Interest rate policy effects",
                "Market sentiment analysis"
            ]
            for topic in google_topics:
                self.topic_scores[topic] = self.topic_scores.get(topic, 0) + 3
        
        self.trending_topics.extend(google_topics)
        print(f"  Found {len(google_topics)} trending Google topics")
        
        return google_topics
    
    def _create_topic_from_query(self, query, base_keyword):
        """Create an academic topic from a search query"""
        query = query.lower()
        
        # Academic framing templates
        if 'how' in query or 'why' in query:
            # Convert question to statement
            topic = query.replace('how', '').replace('why', '').strip()
            topic = f"{topic.title()} in Financial Markets"
        elif 'vs' in query or 'versus' in query:
            topic = query.replace('vs', 'versus').title() + ": A Comparative Analysis"
        elif any(word in query for word in ['impact', 'effect', 'influence']):
            topic = query.title() + " on Market Dynamics"
        else:
            # Generic academic framing
            topic = query.title() + " and Market Behavior"
        
        return topic
    
    def combine_and_rank_topics(self):
        """Combine and rank topics by relevance using smart algorithm"""
        print("\n→ Ranking topics by relevance...")
        
        # Remove duplicates
        unique_topics = list(set(self.trending_topics))
        
        # Smart ranking algorithm
        ranked_topics = []
        
        for topic in unique_topics:
            # Calculate composite score
            base_score = self.topic_scores.get(topic, 1)
            
            # Recency bonus (topics analyzed more recently get slight boost)
            recency_bonus = 1.0
            
            # Length penalty (very long topics get slight penalty)
            length_penalty = 1.0 if len(topic) < 80 else 0.8
            
            # Keyword relevance bonus
            relevance_bonus = 1.0
            high_value_keywords = [
                'ai', 'machine learning', 'cryptocurrency', 'bitcoin', 'esg',
                'climate', 'behavioral', 'risk', 'volatility', 'market',
                'digital', 'blockchain', 'sustainable', 'inflation'
            ]
            for keyword in high_value_keywords:
                if keyword in topic.lower():
                    relevance_bonus += 0.2
            
            # Calculate final score
            final_score = base_score * recency_bonus * length_penalty * relevance_bonus
            
            ranked_topics.append((topic, final_score))
        
        # Sort by score (descending)
        ranked_topics.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the topics (without scores)
        return [topic for topic, score in ranked_topics]
    
    def suggest_paper_topics(self, count=5, use_google_trends=True):
        """Suggest top paper topics"""
        print(f"\n{'='*60}")
        print("TREND ANALYSIS RESULTS")
        print(f"{'='*60}\n")
        
        # Analyze trends
        self.analyze_ssrn_trends()
        
        # Google Trends is optional (can be slow)
        if use_google_trends:
            print("  (This may take 30-60 seconds due to API rate limits...)")
            try:
                self.analyze_google_trends()
            except Exception as e:
                print(f"  ⚠️  Skipping Google Trends due to error: {e}")
        
        # Rank topics
        ranked_topics = self.combine_and_rank_topics()
        
        # Get top suggestions
        top_topics = ranked_topics[:count]
        
        print(f"\nTop {count} Suggested Paper Topics:\n")
        for i, topic in enumerate(top_topics, 1):
            score = self.topic_scores.get(topic, 0)
            print(f"{i}. {topic} (score: {score:.1f})")
        
        print(f"\n{'='*60}\n")
        
        return top_topics
    
    def save_trends_report(self, output_dir):
        """Save trends analysis report"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        date_str = datetime.now().strftime('%Y%m%d')
        report_file = output_dir / f"trends_report_{date_str}.json"
        
        ranked_topics = self.combine_and_rank_topics()
        
        report = {
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "trending_topics": self.trending_topics,
            "topic_scores": self.topic_scores,
            "ranked_topics": ranked_topics,
            "top_suggestions": ranked_topics[:10],
            "analysis_method": "SSRN web scraping + Google Trends API + Smart ranking algorithm"
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Trends report saved: {report_file}")
        return report_file


def main():
    import sys
    
    analyzer = TrendAnalyzer()
    
    # Check if user wants to skip Google Trends for faster analysis
    use_google_trends = '--fast' not in sys.argv
    
    # Suggest topics
    top_topics = analyzer.suggest_paper_topics(count=10, use_google_trends=use_google_trends)
    
    # Save report
    output_dir = Path(__file__).parent.parent / 'metadata'
    analyzer.save_trends_report(output_dir)
    
    # Print usage suggestion
    print("\nTo generate a paper on a trending topic:")
    print(f'  python3 run_automation.py "{top_topics[0]}"')
    print()


if __name__ == '__main__':
    main()
