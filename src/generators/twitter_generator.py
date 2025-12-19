import random
import re
from typing import Dict, List, Optional
from src.llm.prompt_templates import build_format_prompt, build_refine_prompt, get_system_prompt
from src.utils.config import Config

# Optional RAG import - may not be available on all Python versions
try:
    from src.rag.retriever import Retriever
    RAG_AVAILABLE = True
except ImportError:
    Retriever = None
    RAG_AVAILABLE = False


class TwitterGenerator:
    """Generate Twitter/X posts with stoic perspective using 70/20/10 engagement strategy."""

    def __init__(self, llm_client, retriever=None, config: Config = None):
        self.llm = llm_client
        self.retriever = retriever
        self.config = config or Config

    def _select_format(self) -> str:
        """Weighted random selection based on 70/20/10 engagement strategy."""
        weights = self.config.POST_FORMAT_WEIGHTS
        total = sum(weights.values())
        roll = random.randint(1, total)

        cumulative = 0
        for format_type, weight in weights.items():
            cumulative += weight
            if roll <= cumulative:
                return format_type

        return "short"

    def _select_virtue(self) -> str:
        """Randomly select a stoic virtue."""
        return random.choice(self.config.VIRTUES)

    def _get_max_tokens(self, format_type: str) -> int:
        """Get the appropriate max_tokens for a format type."""
        token_limits = {
            "short": self.config.SHORT_MAX_TOKENS,
            "thread": self.config.THREAD_MAX_TOKENS,
            "long": self.config.LONG_MAX_TOKENS,
            "reply": self.config.SHORT_MAX_TOKENS,
        }
        return token_limits.get(format_type, self.config.TWEET_MAX_TOKENS)

    def generate(
        self,
        topic: str = None,
        model_name: str = "gpt4",
        include_examples: bool = True,
        format_type: str = None,
        virtue: str = None,
    ) -> Dict:
        """
        Generate Twitter/X content based on format type and virtue.

        Args:
            topic: The topic for the content
            model_name: Which model to use ('claude' or 'gpt4')
            include_examples: Whether to include style examples (only for threads)
            format_type: 'short', 'thread', 'long', or None for weighted random
            virtue: 'wisdom', 'courage', 'justice', 'temperance', 'general', or None for random

        Returns:
            Dictionary with content, format_type, virtue, tweets array, and metadata
        """
        if format_type is None:
            format_type = self._select_format()

        if virtue is None:
            virtue = self._select_virtue()

        if not topic:
            topic = self._get_random_topic(virtue)

        knowledge_context = ""
        knowledge_results = []
        style_context = ""

        if self.retriever:
            knowledge_k = 1 if format_type == "short" else max(1, self.config.RETRIEVAL_K // 2)
            knowledge_results = self.retriever.retrieve_knowledge(topic, k=knowledge_k)
            knowledge_context = self.retriever.format_knowledge_context(knowledge_results)

            if include_examples and format_type == "thread":
                style_results = self.retriever.retrieve_style_examples(
                    "twitter tweet thread", k=self.config.STYLE_EXAMPLES_K
                )
                style_context = self.retriever.format_style_examples(style_results)

        prompt = build_format_prompt(
            format_type=format_type,
            topic=topic,
            knowledge_context=knowledge_context,
            style_examples=style_context,
            virtue=virtue,
        )

        system_prompt = get_system_prompt("twitter", virtue)

        try:
            raw_content = self.llm.generate(
                prompt=prompt,
                system=system_prompt,
                max_tokens=self._get_max_tokens(format_type),
                temperature=self.config.SOCIAL_TEMPERATURE,
            )

            content, tweets = self._parse_content(raw_content, format_type)

        except Exception as e:
            return {
                "error": str(e),
                "content": None,
                "format_type": format_type,
                "virtue": virtue,
                "tweets": [],
                "citations": None,
            }

        citations = self.retriever.format_citations(knowledge_results) if self.retriever else None

        return {
            "content": content,
            "format_type": format_type,
            "virtue": virtue,
            "tweets": tweets,
            "raw_content": raw_content,
            "citations": citations,
            "topic": topic,
            "model": model_name,
            "tweet_count": len(tweets) if tweets else 1,
            "knowledge_sources": len(knowledge_results),
        }

    def generate_reply(
        self,
        original_content: str,
        username: str,
        topic: str = None,
        model_name: str = "gpt4",
        virtue: str = None,
    ) -> Dict:
        """Generate a reply to a tweet. Always 280 chars or less."""
        search_topic = topic or original_content[:100]

        if virtue is None:
            virtue = self._select_virtue()

        knowledge_context = ""
        knowledge_results = []

        if self.retriever:
            knowledge_results = self.retriever.retrieve_knowledge(search_topic, k=1)
            knowledge_context = self.retriever.format_knowledge_context(knowledge_results)

        prompt = build_format_prompt(
            format_type="reply",
            topic=search_topic,
            knowledge_context=knowledge_context,
            original_content=original_content,
            username=username,
            virtue=virtue,
        )

        system_prompt = get_system_prompt("twitter", virtue)

        try:
            raw_content = self.llm.generate(
                prompt=prompt,
                system=system_prompt,
                max_tokens=self.config.SHORT_MAX_TOKENS,
                temperature=self.config.SOCIAL_TEMPERATURE,
            )

            reply = self._clean_reply(raw_content)

        except Exception as e:
            return {
                "error": str(e),
                "content": None,
                "format_type": "reply",
                "virtue": virtue,
            }

        citations = self.retriever.format_citations(knowledge_results) if self.retriever else None

        return {
            "content": reply,
            "format_type": "reply",
            "virtue": virtue,
            "tweets": [reply],
            "raw_content": raw_content,
            "citations": citations,
            "model": model_name,
            "reply_to_username": username,
        }

    def refine(
        self,
        content: str,
        instruction: str,
        model_name: str = "gpt4",
    ) -> Dict:
        """Refine existing content based on user instruction."""
        prompt = build_refine_prompt(content, instruction)
        system_prompt = get_system_prompt("twitter")

        try:
            refined = self.llm.generate(
                prompt=prompt,
                system=system_prompt,
                max_tokens=self.config.THREAD_MAX_TOKENS,
                temperature=0.7,
            )

            refined = refined.strip().strip('"\'')

        except Exception as e:
            return {
                "error": str(e),
                "content": None,
                "original": content,
            }

        return {
            "content": refined,
            "original": content,
            "instruction": instruction,
            "model": model_name,
        }

    def _parse_content(self, raw_content: str, format_type: str) -> tuple:
        """Parse content based on format type."""
        raw_content = raw_content.strip()

        if format_type == "short":
            content = self._clean_short_tweet(raw_content)
            return content, [content]

        elif format_type == "thread":
            tweets = self._parse_thread_tweets(raw_content)
            combined = "\n\n".join(tweets)
            return combined, tweets

        elif format_type == "long":
            content = self._clean_long_post(raw_content)
            return content, [content]

        else:
            return raw_content, [raw_content]

    def _clean_short_tweet(self, content: str) -> str:
        """Clean up a short tweet response."""
        content = re.sub(r'^[\d\.\-\)\s]+', '', content)
        content = content.strip('"\'')
        if len(content) > 280:
            content = content[:277] + "..."
        return content.strip()

    def _parse_thread_tweets(self, content: str) -> List[str]:
        """Parse numbered thread tweets from response."""
        tweets = []

        pattern = r'(?:^|\n)\s*(\d+)[\/\.\)]\s*'
        parts = re.split(pattern, content)

        if len(parts) > 2:
            for i in range(2, len(parts), 2):
                tweet = parts[i].strip()
                if tweet:
                    tweet = tweet.strip('"\'')
                    if len(tweet) > 280:
                        tweet = tweet[:277] + "..."
                    tweets.append(tweet)

        if not tweets:
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    tweet = re.sub(r'^[\d\.\-\/\)\s]+', '', line).strip()
                    if tweet:
                        tweets.append(tweet)

        return tweets if tweets else [content]

    def _clean_long_post(self, content: str) -> str:
        """Clean up a long-form post."""
        content = content.strip('"\'')
        content = re.sub(r'\n{3,}', '\n\n', content)
        return content.strip()

    def _clean_reply(self, content: str) -> str:
        """Clean and validate a reply."""
        content = content.strip('"\'')
        content = re.sub(r'^[\d\.\-\)\s]+', '', content)
        if len(content) > 280:
            content = content[:277] + "..."
        return content.strip()

    def _get_random_topic(self, virtue: str = None) -> str:
        """Get a random stoic topic, optionally filtered by virtue."""
        virtue_topics = {
            "wisdom": [
                "practical wisdom in daily decisions",
                "discernment between good and bad",
                "clear thinking without bias",
                "understanding what truly matters",
            ],
            "courage": [
                "facing fears with composure",
                "standing up for what's right",
                "enduring hardship gracefully",
                "speaking truth when difficult",
            ],
            "justice": [
                "treating others with dignity",
                "fulfilling duties to community",
                "fairness in daily interactions",
                "contributing to the common good",
            ],
            "temperance": [
                "self-control in modern life",
                "moderation with technology",
                "mastering impulses and reactions",
                "finding balance in desires",
            ],
            "general": [
                "amor fati - loving your fate",
                "memento mori - awareness of mortality",
                "dichotomy of control",
                "living according to nature",
                "finding inner peace",
                "building resilience",
            ],
        }

        if virtue and virtue in virtue_topics:
            return random.choice(virtue_topics[virtue])

        all_topics = []
        for topics in virtue_topics.values():
            all_topics.extend(topics)
        return random.choice(all_topics)
