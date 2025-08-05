"""
Simulated Translation for Vaani Sentinel X
Task 4 Component 3: Simulated Multilingual Preview Generator
Provides dummy translations for preview (hardcoded strings as per Task 4)
"""

import json
import random
from typing import Dict, List, Any, Optional

class SimulatedTranslator:
    """
    Simulated translation system for Task 4
    Uses hardcoded dummy translations for preview purposes
    Real LLM translation will be implemented in Task 5
    """
    
    def __init__(self):
        # Dummy translation templates for Task 4 simulation
        self.translation_templates = {
            # Sample content templates with dummy translations
            "mindfulness": {
                "en": "Embrace mindfulness and find inner peace through meditation",
                "hi": "ध्यान के माध्यम से मानसिक शांति और आंतरिक शांति प्राप्त करें",
                "sa": "ध्यान द्वारा मानसिक स्थिरता और अन्तः शान्ति प्राप्त करें",
                "mr": "ध्यानाद्वारे मानसिक शांती आणि अंतर्गत शांती मिळवा",
                "es": "Abraza la atención plena y encuentra la paz interior a través de la meditación",
                "fr": "Embrassez la pleine conscience et trouvez la paix intérieure par la méditation",
                "de": "Umarme Achtsamkeit und finde inneren Frieden durch Meditation",
                "ja": "マインドフルネスを受け入れ、瞑想を通じて内なる平和を見つけましょう",
                "zh": "拥抱正念，通过冥想找到内心的平静"
            },
            "wisdom": {
                "en": "Knowledge is power, but wisdom is knowing how to use it",
                "hi": "ज्ञान शक्ति है, लेकिन बुद्धि यह जानना है कि इसका उपयोग कैसे करें",
                "sa": "ज्ञानं बलम्, किन्तु प्रज्ञा तस्य उपयोगस्य विधिः",
                "mr": "ज्ञान ही शक्ती आहे, परंतु बुद्धी म्हणजे त्याचा वापर कसा करावा हे जाणणे",
                "es": "El conocimiento es poder, pero la sabiduría es saber cómo usarlo",
                "fr": "La connaissance est le pouvoir, mais la sagesse est de savoir comment l'utiliser",
                "de": "Wissen ist Macht, aber Weisheit ist zu wissen, wie man es nutzt",
                "ja": "知識は力ですが、知恵はそれをどう使うかを知ることです",
                "zh": "知识就是力量，但智慧是知道如何运用它"
            },
            "gratitude": {
                "en": "Gratitude transforms ordinary moments into extraordinary blessings",
                "hi": "कृतज्ञता साधारण क्षणों को असाधारण आशीर्वाद में बदल देती है",
                "sa": "कृतज्ञता सामान्य क्षणान् असामान्य आशीर्वादेषु परिवर्तयति",
                "mr": "कृतज्ञता सामान्य क्षणांना असामान्य आशीर्वादात रूपांतरित करते",
                "es": "La gratitud transforma momentos ordinarios en bendiciones extraordinarias",
                "fr": "La gratitude transforme les moments ordinaires en bénédictions extraordinaires",
                "de": "Dankbarkeit verwandelt gewöhnliche Momente in außergewöhnliche Segnungen",
                "ja": "感謝は普通の瞬間を特別な祝福に変えます",
                "zh": "感恩将平凡的时刻转化为非凡的祝福"
            },
            "success": {
                "en": "Success is not final, failure is not fatal: it is the courage to continue that counts",
                "hi": "सफलता अंतिम नहीं है, असफलता घातक नहीं है: जारी रखने का साहस ही मायने रखता है",
                "sa": "सफलता अन्तिमः न, असफलता घातकः न: निरन्तरता साहसः एव महत्त्वपूर्णः",
                "mr": "यश अंतिम नाही, अपयश घातक नाही: चालू ठेवण्याचे धैर्यच महत्त्वाचे आहे",
                "es": "El éxito no es definitivo, el fracaso no es fatal: es el coraje de continuar lo que cuenta",
                "fr": "Le succès n'est pas définitif, l'échec n'est pas fatal : c'est le courage de continuer qui compte",
                "de": "Erfolg ist nicht endgültig, Misserfolg ist nicht tödlich: Es ist der Mut weiterzumachen, der zählt",
                "ja": "成功は最終的ではなく、失敗は致命的ではありません：続ける勇気こそが重要です",
                "zh": "成功不是终点，失败不是致命的：重要的是继续前进的勇气"
            },
            "peace": {
                "en": "Peace comes from within. Do not seek it without",
                "hi": "शांति भीतर से आती है। इसे बाहर मत खोजो",
                "sa": "शान्तिः अन्तरतः आगच्छति। बहिः मा अन्विष्यताम्",
                "mr": "शांती आतून येते. ती बाहेर शोधू नका",
                "es": "La paz viene de adentro. No la busques afuera",
                "fr": "La paix vient de l'intérieur. Ne la cherchez pas à l'extérieur",
                "de": "Frieden kommt von innen. Suche ihn nicht außerhalb",
                "ja": "平和は内側から来ます。外に求めてはいけません",
                "zh": "和平来自内心。不要在外面寻找"
            }
        }
        
        # Platform-specific formatting templates
        self.platform_formats = {
            "twitter": {
                "max_length": 280,
                "hashtag_style": "#",
                "mention_style": "@",
                "format": "{content} {hashtags}"
            },
            "instagram": {
                "max_length": 2200,
                "hashtag_style": "#",
                "mention_style": "@",
                "format": "{content}\n\n{hashtags}\n\n{call_to_action}"
            },
            "linkedin": {
                "max_length": 3000,
                "hashtag_style": "#",
                "mention_style": "@",
                "format": "{content}\n\n{hashtags}\n\n{professional_note}"
            }
        }
    
    def simulate_translation(
        self,
        content_text: str,
        target_language: str,
        source_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Simulate translation using hardcoded dummy translations
        Task 4 implementation - no real NLP/LLM yet
        """
        
        # Find best matching template
        best_match = self._find_best_template_match(content_text)
        
        if best_match and target_language in self.translation_templates[best_match]:
            # Use template translation
            translated_text = self.translation_templates[best_match][target_language]
            confidence = 0.9  # High confidence for template matches
            method = "template_based"
        else:
            # Generate placeholder translation
            translated_text = self._generate_placeholder_translation(content_text, target_language)
            confidence = 0.6  # Lower confidence for placeholders
            method = "placeholder_generated"
        
        return {
            "original_text": content_text,
            "translated_text": translated_text,
            "source_language": source_language,
            "target_language": target_language,
            "confidence": confidence,
            "translation_method": method,
            "template_used": best_match,
            "is_simulation": True,
            "note": "Task 4 simulation - real LLM translation in Task 5"
        }
    
    def _find_best_template_match(self, content_text: str) -> Optional[str]:
        """Find the best matching translation template"""
        
        content_lower = content_text.lower()
        
        # Simple keyword matching for templates
        template_keywords = {
            "mindfulness": ["mindfulness", "meditation", "peace", "inner", "calm"],
            "wisdom": ["knowledge", "wisdom", "power", "learn", "understand"],
            "gratitude": ["gratitude", "grateful", "thankful", "blessing", "appreciate"],
            "success": ["success", "failure", "courage", "continue", "achieve"],
            "peace": ["peace", "within", "inside", "seek", "find"]
        }
        
        best_match = None
        max_matches = 0
        
        for template, keywords in template_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            if matches > max_matches:
                max_matches = matches
                best_match = template
        
        return best_match if max_matches > 0 else None
    
    def _generate_placeholder_translation(self, content_text: str, target_language: str) -> str:
        """Generate placeholder translation for content not in templates"""
        
        language_placeholders = {
            "hi": f"[हिंदी अनुवाद: {content_text[:30]}...]",
            "sa": f"[संस्कृत अनुवाद: {content_text[:30]}...]",
            "mr": f"[मराठी भाषांतर: {content_text[:30]}...]",
            "gu": f"[ગુજરાતી અનુવાદ: {content_text[:30]}...]",
            "ta": f"[தமிழ் மொழிபெயர்ப்பு: {content_text[:30]}...]",
            "te": f"[తెలుగు అనువాదం: {content_text[:30]}...]",
            "kn": f"[ಕನ್ನಡ ಅನುವಾದ: {content_text[:30]}...]",
            "ml": f"[മലയാളം വിവർത്തനം: {content_text[:30]}...]",
            "bn": f"[বাংলা অনুবাদ: {content_text[:30]}...]",
            "pa": f"[ਪੰਜਾਬੀ ਅਨੁਵਾਦ: {content_text[:30]}...]",
            "es": f"[Traducción al español: {content_text[:30]}...]",
            "fr": f"[Traduction française: {content_text[:30]}...]",
            "de": f"[Deutsche Übersetzung: {content_text[:30]}...]",
            "it": f"[Traduzione italiana: {content_text[:30]}...]",
            "pt": f"[Tradução portuguesa: {content_text[:30]}...]",
            "ru": f"[Русский перевод: {content_text[:30]}...]",
            "ja": f"[日本語翻訳: {content_text[:30]}...]",
            "ko": f"[한국어 번역: {content_text[:30]}...]",
            "zh": f"[中文翻译: {content_text[:30]}...]"
        }
        
        return language_placeholders.get(target_language, f"[Translation to {target_language}: {content_text[:30]}...]")
    
    def generate_multilingual_preview(
        self,
        content_text: str,
        target_languages: List[str],
        platform: str = "twitter",
        source_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate multilingual preview for multiple languages
        Task 4 Component 3 implementation
        """
        
        previews = {}
        platform_format = self.platform_formats.get(platform, self.platform_formats["twitter"])
        
        for language in target_languages:
            # Get simulated translation
            translation_result = self.simulate_translation(content_text, language, source_language)
            
            # Format for platform
            formatted_content = self._format_for_platform(
                translation_result["translated_text"], 
                platform, 
                language
            )
            
            previews[language] = {
                "language": language,
                "original_text": content_text,
                "translated_text": translation_result["translated_text"],
                "formatted_content": formatted_content,
                "platform": platform,
                "confidence": translation_result["confidence"],
                "translation_method": translation_result["translation_method"],
                "character_count": len(formatted_content),
                "max_length": platform_format["max_length"],
                "within_limits": len(formatted_content) <= platform_format["max_length"],
                "is_simulation": True
            }
        
        return {
            "source_content": content_text,
            "source_language": source_language,
            "target_languages": target_languages,
            "platform": platform,
            "previews": previews,
            "total_languages": len(target_languages),
            "simulation_note": "Task 4 dummy translations - real LLM in Task 5"
        }
    
    def _format_for_platform(self, content: str, platform: str, language: str) -> str:
        """Format content for specific platform"""
        
        platform_format = self.platform_formats.get(platform, self.platform_formats["twitter"])
        
        # Generate appropriate hashtags for language
        hashtags = self._generate_hashtags(language, platform)
        
        if platform == "twitter":
            formatted = f"{content} {hashtags}"
        elif platform == "instagram":
            call_to_action = self._get_call_to_action(language)
            formatted = f"{content}\n\n{hashtags}\n\n{call_to_action}"
        elif platform == "linkedin":
            professional_note = self._get_professional_note(language)
            formatted = f"{content}\n\n{hashtags}\n\n{professional_note}"
        else:
            formatted = f"{content} {hashtags}"
        
        # Trim if too long
        max_length = platform_format["max_length"]
        if len(formatted) > max_length:
            formatted = formatted[:max_length-3] + "..."
        
        return formatted
    
    def _generate_hashtags(self, language: str, platform: str) -> str:
        """Generate appropriate hashtags for language and platform"""
        
        hashtag_sets = {
            "en": ["#Mindfulness", "#Wisdom", "#Peace"],
            "hi": ["#मानसिकशांति", "#ज्ञान", "#शांति"],
            "sa": ["#ध्यान", "#ज्ञान", "#शान्ति"],
            "mr": ["#मानसिकशांती", "#ज्ञान", "#शांती"],
            "es": ["#Sabiduría", "#Paz", "#Meditación"],
            "fr": ["#Sagesse", "#Paix", "#Méditation"],
            "de": ["#Weisheit", "#Frieden", "#Meditation"],
            "ja": ["#知恵", "#平和", "#瞑想"],
            "zh": ["#智慧", "#和平", "#冥想"]
        }
        
        hashtags = hashtag_sets.get(language, hashtag_sets["en"])
        return " ".join(hashtags[:2])  # Limit hashtags for readability
    
    def _get_call_to_action(self, language: str) -> str:
        """Get call to action text for language"""
        
        cta_texts = {
            "en": "Share your thoughts in the comments! 💭",
            "hi": "अपने विचार कमेंट में साझा करें! 💭",
            "sa": "अपने विचारान् टिप्पणीषु साझां कुर्वन्तु! 💭",
            "mr": "तुमचे विचार कमेंटमध्ये शेअर करा! 💭",
            "es": "¡Comparte tus pensamientos en los comentarios! 💭",
            "fr": "Partagez vos pensées dans les commentaires ! 💭",
            "de": "Teilt eure Gedanken in den Kommentaren! 💭",
            "ja": "コメントであなたの考えを共有してください！💭",
            "zh": "在评论中分享您的想法！💭"
        }
        
        return cta_texts.get(language, cta_texts["en"])
    
    def _get_professional_note(self, language: str) -> str:
        """Get professional note for LinkedIn"""
        
        professional_notes = {
            "en": "What are your thoughts on this? Let's discuss in the comments.",
            "hi": "इस पर आपके क्या विचार हैं? आइए कमेंट में चर्चा करते हैं।",
            "sa": "अस्मिन् विषये भवतां किं मतम्? टिप्पणीषु चर्चां कुर्मः।",
            "mr": "यावर तुमचे काय मत आहे? कमेंटमध्ये चर्चा करूया।",
            "es": "¿Cuáles son sus pensamientos sobre esto? Discutamos en los comentarios.",
            "fr": "Quelles sont vos réflexions à ce sujet ? Discutons dans les commentaires.",
            "de": "Was sind eure Gedanken dazu? Lasst uns in den Kommentaren diskutieren.",
            "ja": "これについてどう思いますか？コメントで議論しましょう。",
            "zh": "您对此有何看法？让我们在评论中讨论。"
        }
        
        return professional_notes.get(language, professional_notes["en"])

# Global simulated translator instance
simulated_translator = SimulatedTranslator()

def get_simulated_translator() -> SimulatedTranslator:
    """Get the global simulated translator instance"""
    return simulated_translator
