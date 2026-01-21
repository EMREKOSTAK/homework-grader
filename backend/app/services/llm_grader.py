"""LLM Grader Service - AI-powered grading with structured output."""

import json
import os
import re
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI
from pydantic import ValidationError

from app.models.schemas import (
    ParsedPPTX,
    GradingResult,
    RubricScore,
    EvidenceItem,
    ImprovementSuggestion,
    LLMGradingResponse,
    DetectedEthicsPrinciple,
)

logger = logging.getLogger(__name__)

# The comprehensive grading prompt in Turkish
GRADING_SYSTEM_PROMPT = """Sen bir üniversite etik dersi ödev değerlendirme uzmanısın. Öğrenci sunumlarını (PowerPoint) derinlemesine analiz edip değerlendiriyorsun.

## GÖREV
Verilen sunum içeriğini aşağıdaki rubriğe göre kapsamlı şekilde değerlendir. Tüm değerlendirmeyi sen yapacaksın.

## ÖNEMLİ NOT
Filmin gerçek sahnelerini bilemeyebilirsin. Bu nedenle:
- Sahnenin gerçekten filmde olup olmadığını doğrulayamazsın
- AMA şunları değerlendirebilirsin:
  * Açıklamanın kendi içinde tutarlı olup olmadığı
  * Anlatımın mantıksal bütünlüğü
  * Etik ilke ile sahne arasındaki bağlantının mantıklı olup olmadığı
  * Yazının kalitesi ve akademik düzeyi

## RUBRİK (Toplam 100 puan)

### 1. ETİK İLKELERİ DOĞRULUĞU VE UYGULAMASI (15 puan)

Öğrencinin sunumunda hangi etik ilkelerinden bahsettiğini bul ve değerlendir:

a) İLKE TANIMI DOĞRULUĞU (5 puan):
   - Etik ilkesi doğru tanımlanmış mı?
   - Tanım akademik/felsefi açıdan kabul edilebilir mi?
   - Yanlış veya eksik tanımlar varsa puan düşür

b) İLKE-SAHNE UYUMU (5 puan):
   - Verilen sahne gerçekten bu etik ilkeyi yansıtıyor mu?
   - Öğrenci doğru etik ilkeyi mi seçmiş?

c) AÇIKLAMA KALİTESİ (5 puan):
   - Etik ilke ile sahne arasındaki bağlantı açık mı?
   - Mantıksal çıkarım doğru mu?

Minimum 5 farklı etik ilkesi gerekli. 5'ten az varsa ciddi puan kesintisi yap.

### 2. SAHNE AÇIKLAMASI KALİTESİ (50 puan)

a) ÖZGÜLLÜK VE DETAY (0-20 puan):
   - Sahne somut ve detaylı anlatılmış mı?
   - Karakterlerin isimleri, diyaloglar, olayların sırası var mı?

b) İÇ TUTARLILIK (0-15 puan):
   - Anlatılan olaylar kendi içinde tutarlı mı?
   - Mantık hataları veya çelişkiler var mı?

c) ETİK BAĞLANTISI (0-15 puan):
   - Sahne ile etik ilke arasındaki bağ açıkça kurulmuş mu?
   - Analiz yüzeysel mi derin mi?

### 3. ŞABLON UYUMU (15 puan)

Sunumda şu alanları ara:
- Film adı (2 puan)
- Tür/Genre (2 puan)
- Yönetmen (2 puan)
- Senarist (1 puan)
- Oyuncular (1 puan)
- Kişisel düşünceler/değerlendirme (2 puan)
- Sayfa numaraları (2 puan)
- Genel düzen ve format (3 puan)

### 4. GÖRSEL TASARIM VE SUNUM KALİTESİ (10 puan)

a) METİN KALİTESİ (5 puan):
   - Yazım ve dilbilgisi hataları
   - Akademik dil kullanımı

b) DÜZEN (5 puan):
   - Bilgi mantıklı organize edilmiş mi?
   - Profesyonel görünüm

### 5. ZAMANINDA TESLİM (10 puan)
- Bu kısım manuel olarak belirlenir, sen 0 puan ver

## DEĞERLENDİRME PRENSİPLERİ

1. Her puan için sunumdan somut alıntı (slayt numarası + metin) göster
2. Nesnel ol, kişisel görüşlerden kaçın
3. Yapıcı iyileştirme önerileri ver
4. Filmi bilmemen dezavantaj olmamalı - tutarlılık ve mantığı değerlendir

## JSON ÇIKTI FORMATI

{
  "toplam_puan": 75,
  "rubrik_puanlari": [
    {
      "kategori": "Etik Ilkeleri",
      "puan": 12,
      "max_puan": 15,
      "aciklama": "Degerlendirme aciklamasi",
      "kanitlar": [{"slayt_no": 1, "alinti": "Ornek alinti", "yorum": "Yorum"}],
      "alt_puanlar": {"ilke_tanimi": 4, "sahne_uyumu": 4, "aciklama": 4},
      "tespit_edilen_ilkeler": [{"ilke": "Adalet", "dogru_tanim": true, "sahne_uyumu": true, "not": "Aciklama"}]
    },
    {
      "kategori": "Sahne Aciklamasi",
      "puan": 35,
      "max_puan": 50,
      "aciklama": "Sahne degerlendirmesi",
      "kanitlar": [{"slayt_no": 2, "alinti": "Sahne alintisi", "yorum": "Yorum"}],
      "alt_puanlar": {"ozgulluk": 15, "tutarlilik": 10, "etik_baglantisi": 10},
      "tutarlilik_analizi": "Tutarlilik analizi"
    },
    {
      "kategori": "Sablon Uyumu",
      "puan": 12,
      "max_puan": 15,
      "aciklama": "Sablon degerlendirmesi",
      "kanitlar": [{"slayt_no": 1, "alinti": "Film adi vs"}],
      "alt_puanlar": {"alanlar": 8, "format": 4},
      "bulunan_alanlar": ["Film adi", "Yonetmen"],
      "eksik_alanlar": ["Senarist"]
    },
    {
      "kategori": "Gorsel Tasarim",
      "puan": 7,
      "max_puan": 10,
      "aciklama": "Tasarim degerlendirmesi",
      "kanitlar": [],
      "alt_puanlar": {"metin": 4, "duzen": 3},
      "dil_hatalari": []
    }
  ],
  "eksik_ogeler": ["Eksik oge 1"],
  "iyilestirme_onerileri": [{"kategori": "Genel", "oneri": "Oneri metni", "oncelik": "orta"}],
  "genel_degerlendirme": "Genel degerlendirme metni",
  "notlar": ""
}

ONEMLI: Sadece gecerli JSON dondur. JSON disinda metin olmasin."""


GRADING_USER_PROMPT_TEMPLATE = """Aşağıdaki öğrenci sunumunu değerlendir:

=== SUNUM İÇERİĞİ ===
{slide_content}

=== SUNUM BİLGİLERİ ===
Toplam slayt sayısı: {slide_count}
Toplam karakter sayısı: {char_count}

Lütfen yukarıdaki rubriğe göre JSON formatında değerlendirme yap."""


FIX_JSON_PROMPT = """Önceki yanıtın geçerli JSON formatında değildi. Lütfen aşağıdaki hatayı düzelt ve SADECE geçerli JSON döndür:

Hata: {error}

Beklenen format için sistem mesajındaki JSON şemasına bak."""


class LLMGrader:
    """Handles LLM-based grading of presentations."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        if not self.api_key:
            logger.warning("No API key provided. LLM grading will not work.")

    def _get_client(self) -> OpenAI:
        kwargs = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return OpenAI(**kwargs)

    def _format_slide_content(self, parsed_pptx: ParsedPPTX) -> str:
        parts = []
        for slide in parsed_pptx.slides:
            parts.append(f"\n[Slayt {slide.slide_no}]")
            for element in slide.elements:
                parts.append(f"  • {element.raw_text}")
        return "\n".join(parts)

    def _get_char_count(self, parsed_pptx: ParsedPPTX) -> int:
        total = 0
        for slide in parsed_pptx.slides:
            for element in slide.elements:
                total += len(element.text)
        return total

    def _parse_llm_response(self, response_text: str) -> LLMGradingResponse:
        text = response_text.strip()

        # Remove markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        # Find JSON object
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx:end_idx + 1]

        # Fix common JSON issues
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)

        data = json.loads(text)
        return LLMGradingResponse(**data)

    def _convert_to_grading_result(
        self,
        llm_response: LLMGradingResponse,
        on_time: bool,
    ) -> GradingResult:
        rubric_scores = []

        for llm_score in llm_response.rubrik_puanlari:
            evidence = []
            for ev in llm_score.kanitlar:
                if isinstance(ev, dict):
                    evidence.append(EvidenceItem(
                        slide_no=ev.get("slayt_no", 0),
                        quote=ev.get("alinti", ""),
                        context=None,
                        comment=ev.get("yorum"),
                    ))

            sub_scores = llm_score.alt_puanlar if llm_score.alt_puanlar else None

            detected_principles = None
            if llm_score.tespit_edilen_ilkeler:
                detected_principles = []
                for p in llm_score.tespit_edilen_ilkeler:
                    if isinstance(p, dict):
                        detected_principles.append(DetectedEthicsPrinciple(
                            principle=p.get("ilke", ""),
                            correct_definition=p.get("dogru_tanim", True),
                            scene_match=p.get("sahne_uyumu", True),
                            note=p.get("not"),
                        ))

            rubric_scores.append(RubricScore(
                category=llm_score.kategori,
                score=llm_score.puan,
                max_score=llm_score.max_puan,
                reason=llm_score.aciklama,
                evidence=evidence,
                sub_scores=sub_scores,
                detected_principles=detected_principles,
                consistency_analysis=llm_score.tutarlilik_analizi,
                found_fields=llm_score.bulunan_alanlar,
                missing_fields=llm_score.eksik_alanlar,
                language_errors=llm_score.dil_hatalari,
            ))

        # Add on-time score
        on_time_score = 10.0 if on_time else 0.0
        rubric_scores.append(RubricScore(
            category="Zamanında Teslim",
            score=on_time_score,
            max_score=10.0,
            reason="Zamanında teslim edildi" if on_time else "Zamanında teslim edilmedi",
            evidence=[],
            sub_scores=None,
        ))

        total_score = llm_response.toplam_puan + on_time_score

        improvements = []
        for imp in llm_response.iyilestirme_onerileri:
            if isinstance(imp, dict):
                priority_map = {"yuksek": "high", "orta": "medium", "dusuk": "low"}
                improvements.append(ImprovementSuggestion(
                    category=imp.get("kategori", "Genel"),
                    suggestion=imp.get("oneri", ""),
                    priority=priority_map.get(imp.get("oncelik", "orta"), "medium"),
                ))

        return GradingResult(
            total_score=min(100, total_score),
            rubric_scores=rubric_scores,
            missing_items=llm_response.eksik_ogeler,
            improvements=improvements,
            deterministic_checks=[],  # No longer used
            on_time_submitted=on_time,
            grading_notes=llm_response.notlar,
            overall_evaluation=llm_response.genel_degerlendirme,
        )

    async def grade(
        self,
        parsed_pptx: ParsedPPTX,
        on_time: bool = False,
    ) -> GradingResult:
        """Grade a presentation using the LLM."""
        if not self.api_key:
            raise ValueError("API key not configured. Set OPENAI_API_KEY environment variable.")

        client = self._get_client()

        slide_content = self._format_slide_content(parsed_pptx)
        char_count = self._get_char_count(parsed_pptx)

        user_prompt = GRADING_USER_PROMPT_TEMPLATE.format(
            slide_content=slide_content,
            slide_count=parsed_pptx.meta.total_slides,
            char_count=char_count,
        )

        messages = [
            {"role": "system", "content": GRADING_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=4000,
                response_format={"type": "json_object"},
            )
            response_text = response.choices[0].message.content
            llm_response = self._parse_llm_response(response_text)
            return self._convert_to_grading_result(llm_response, on_time)

        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(f"First LLM response invalid, retrying: {e}")

            messages.append({"role": "assistant", "content": response_text})
            messages.append({"role": "user", "content": FIX_JSON_PROMPT.format(error=str(e))})

            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=4000,
                    response_format={"type": "json_object"},
                )
                response_text = response.choices[0].message.content
                llm_response = self._parse_llm_response(response_text)
                return self._convert_to_grading_result(llm_response, on_time)

            except (json.JSONDecodeError, ValidationError) as e2:
                logger.error(f"Second LLM response also invalid: {e2}")
                raise ValueError(f"LLM returned invalid JSON after retry: {e2}")
