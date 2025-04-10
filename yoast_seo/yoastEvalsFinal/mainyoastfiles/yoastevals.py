import re

def evaluate_article(article_content: str, focus_keyword: str):
    focus_keyword_lower = focus_keyword.lower().strip()

    lines = article_content.strip().split('\n')
    
    # Identify headings
    headings = []
    for line in lines:
        if line.startswith('#'):
            headings.append(line.strip())

    # Extract words
    words = re.findall(r"\w+", article_content)
    total_word_count = len(words)

    # Extract sentences
    sentence_candidates = re.split(r'[.?!]+', article_content)
    sentences = [s.strip() for s in sentence_candidates if s.strip()]
    total_sentences = len(sentences)

    # Extract paragraphs
    paragraph_candidates = re.split(r'\n\s*\n', article_content.strip())
    paragraphs = [p.strip() for p in paragraph_candidates if p.strip()]

    # Identify images
    has_image = bool(re.search(r'!\[.*?\]\(.*?\)', article_content)) or bool(re.search(r'<img\s+[^>]*>', article_content))

    # Identify external links
    external_links = re.findall(r'https?://[^\s)]+', article_content)
    external_link_count = len(external_links)

    # Identify internal links
    # Internal links are assumed to be markdown links without http/https
    internal_links = re.findall(r'\[[^\]]*\]\((?!https?://)[^)]+\)', article_content)
    internal_link_count = len(internal_links)

    # -----------------------------
    # Criteria Checks
    # -----------------------------

    # 1. Content Length
    if total_word_count > 900:
        content_length_score = "Green"
    elif 600 <= total_word_count <= 900:
        content_length_score = "Orange"
    else:
        content_length_score = "Red"

    # 2. Outbound Links
    outbound_links_score = "Green" if external_link_count > 0 else "Red"

    # 3. Internal Links
    internal_links_score = "Green" if internal_link_count > 0 else "Red"

    # 4. Images
    images_score = "Green" if has_image else "Red"

    # 5. Keyphrase in Introduction
    introduction = paragraphs[0] if paragraphs else article_content
    intro_first_sentence = re.split(r'[.?!]+', introduction)
    intro_first_sentence = intro_first_sentence[0].strip().lower() if intro_first_sentence else ""
    keyphrase_in_introduction = focus_keyword_lower in intro_first_sentence
    keyphrase_intro_score = "Green" if keyphrase_in_introduction else "Red"

    # 6. Keyphrase Density
    keyword_words = focus_keyword_lower.split()
    count_occurrences = 0
    article_words_lower = [w.lower() for w in words]
    for i in range(len(article_words_lower) - len(keyword_words) + 1):
        if article_words_lower[i:i+len(keyword_words)] == keyword_words:
            count_occurrences += 1
    keyphrase_density = (count_occurrences / total_word_count * 100) if total_word_count > 0 else 0
    if 0.5 <= keyphrase_density <= 2.5:
        keyphrase_density_score = "Green"
    elif 2.5 < keyphrase_density <= 3.0:
        keyphrase_density_score = "Orange"
    else:
        keyphrase_density_score = "Red"

    # 7. Keyphrase Distribution
    segment_size = 150
    segments = [article_words_lower[i:i+segment_size] for i in range(0, len(article_words_lower), segment_size)]
    segment_counts = []
    for seg in segments:
        seg_count = 0
        for i in range(len(seg)-len(keyword_words)+1):
            if seg[i:i+len(keyword_words)] == keyword_words:
                seg_count += 1
        segment_counts.append(seg_count)
    total_occ = sum(segment_counts)
    if total_occ < 4:
        keyphrase_distribution_score = "Red"
    else:
        segments_with_occ = sum(1 for c in segment_counts if c > 0)
        if total_occ >= 6 and segments_with_occ >= len(segments)/2:
            keyphrase_distribution_score = "Green"
        else:
            keyphrase_distribution_score = "Orange"

    # 8. Transition Words
    transition_words = [
        # Addition
        "also", "moreover", "furthermore", "besides", "in addition", "additionally", "what’s more", 
        "not only that", "too", "as well",
        
        # Contrast
        "however", "but", "on the other hand", "yet", "although", "though", "even though", "whereas", 
        "while", "conversely",
        
        # Cause and Effect
        "therefore", "consequently", "as a result", "thus", "hence", "so", "because", "since", 
        "for this reason", "due to",
        
        # Comparison
        "similarly", "likewise", "in the same way", "just as", "equally", "correspondingly", 
        "in like manner", "by the same token",
        
        # Clarification
        "in other words", "that is", "namely", "specifically", "to clarify", "to put it another way",
        
        # Sequence/Order
        "first", "second", "third", "next", "then", "afterwards", "subsequently", "finally", 
        "at last", "in the meantime", "meanwhile", "earlier", "later", "previously",
        
        # Examples/Illustration
        "for example", "for instance", "such as", "including", "to illustrate", "in particular", 
        "specifically", "like",
        
        # Emphasis
        "indeed", "in fact", "certainly", "of course", "without a doubt", "surely", "to be sure", 
        "undoubtedly",
        
        # Summary/Conclusion
        "in conclusion", "to summarize", "in summary", "in short", "in brief", "all in all", "overall", 
        "finally",
        
        # Time
        "before", "after", "during", "while", "as soon as", "once", "until", "when", "whenever", 
        "at the same time", "nowadays",
        
        # Place
        "here", "there", "over there", "nearby", "above", "below", "wherever",
        
        # Concession
        "although", "even though", "though", "granted", "nonetheless", "nevertheless", "still", 
        "despite", "regardless",
        
        # Purpose
        "in order to", "so that", "for the purpose of", "with this in mind", "to this end",
        
        # Condition
        "if", "unless", "provided that", "as long as", "in case",
        
        # Illustration
        "for instance", "such as", "including", "namely", "to illustrate",
        
        # Agreement
        "of course", "certainly", "naturally", "undoubtedly",
        
        # Addition (Informal)
        "plus", "and then", "on top of that",
        
        # Opinion
        "in my opinion", "i believe", "from my perspective", "as i see it",
        
        # Frequency
        "always", "often", "sometimes", "rarely", "never",
        
        # Intensification
        "above all", "beyond", "most importantly", "especially", "chiefly",
        
        # Repetition
        "again", "over and over", "repeatedly", "once more",
        
        # Cause and Reason
        "because of", "owing to", "due to", "as a result of",
        
        # Generalization
        "generally", "overall", "broadly", "as a rule", "on the whole",
        
        # Alternatives
        "or", "alternatively", "otherwise",
        
        # Agreement/Disagreement
        "admittedly", "in contrast", "while it is true", "on the contrary",
        
        # Informal
        "anyway", "by the way", "in any case",
        
        # Formal
        "henceforth", "thereby", "herein",
        
        # Colloquial
        "for starters", "to top it off", "at the end of the day",
        
        # Qualifying
        "almost", "nearly", "sometimes", "possibly", "apparently",
        
        # Conditional
        "supposing", "provided that", "on condition that",
        
        # Contrast (Advanced)
        "albeit", "alike", "distinct",
        
        # Frequency/Intensity
        "rarely", "constantly", "perpetually",
        
        # Opinion (Advanced)
        "it is evident", "undeniably", "arguably",
        
        # Cause/Effect (Formal)
        "consequently", "inevitably", "ergo",
        
        # Conclusion (Advanced)
        "in hindsight", "retrospectively", "to sum up",
        
        # Additive (Advanced)
        "moreover", "what’s more"
    ]
    transition_words = list(set(tw.lower() for tw in transition_words))  # Remove duplicates and lowercase

    sentences_with_transition = 0
    for s in sentences:
        s_lower = s.lower()
        if any(re.search(r'\b' + re.escape(tw) + r'\b', s_lower) for tw in transition_words):
            sentences_with_transition += 1

    transition_percentage = (sentences_with_transition / total_sentences * 100) if total_sentences > 0 else 0
    if transition_percentage < 20:
        transition_score = "Red"
    elif 20 <= transition_percentage < 30:
        transition_score = "Orange"
    else:
        transition_score = "Green"

    # 9. Consecutive Sentences Start with Same Word
    def first_word(sentence):
        w = re.findall(r"\w+", sentence)
        return w[0].lower() if w else ""
    
    first_words = [first_word(s) for s in sentences]
    
    max_consecutive = 1
    current_run = 1
    for i in range(1, len(first_words)):
        if first_words[i] == first_words[i-1] and first_words[i] != "":
            current_run += 1
            max_consecutive = max(max_consecutive, current_run)
        else:
            current_run = 1
    
    if max_consecutive >= 3:
        consecutive_sentences_score = "Red"
    else:
        # Count instances of two consecutive sentences starting with the same word
        pairs_count = 0
        for i in range(1, len(first_words)):
            if first_words[i] == first_words[i-1] and first_words[i] != "":
                pairs_count += 1
        consecutive_sentences_score = "Orange" if pairs_count > 1 else "Green"

    # 10. Subheading Distribution
    # Split article by headings into sections
    heading_indices = [i for i, l in enumerate(lines) if l.strip().startswith('#')]
    sections = []
    if heading_indices:
        for idx in range(len(heading_indices)):
            start = heading_indices[idx] + 1
            end = heading_indices[idx+1] if idx+1 < len(heading_indices) else len(lines)
            section_text = '\n'.join(lines[start:end]).strip()
            if section_text:
                section_words = re.findall(r"\w+", section_text)
                sections.append(len(section_words))
    else:
        # No headings at all, entire article is one section
        sections = [total_word_count]

    long_sections = [wcount for wcount in sections if wcount > 300]
    if len(long_sections) > 1:
        subheading_score = "Red"
    elif len(long_sections) == 1:
        subheading_score = "Orange"
    else:
        subheading_score = "Green"

    # 11. Paragraph Length
    paragraph_scores = []
    for p in paragraphs:
        p_words = re.findall(r"\w+", p)
        p_word_count = len(p_words)
        p_sentences = [s.strip() for s in re.split(r'[.?!]+', p) if s.strip()]
        p_sentence_count = len(p_sentences)
        if p_word_count > 200:
            paragraph_scores.append("Red")
        elif 150 <= p_word_count <= 200:
            paragraph_scores.append("Orange")
        else:
            if p_sentence_count < 3:
                paragraph_scores.append("Red")
            else:
                paragraph_scores.append("Green")
    
    if "Red" in paragraph_scores:
        paragraph_length_score = "Red"
    elif "Orange" in paragraph_scores:
        paragraph_length_score = "Orange"
    else:
        paragraph_length_score = "Green"

    # 12. Sentence Length
    long_sentences = sum(1 for s in sentences if len(re.findall(r"\w+", s)) > 20)
    long_percentage = (long_sentences / total_sentences * 100) if total_sentences > 0 else 0
    if long_percentage <= 25:
        sentence_length_score = "Green"
    elif 25 < long_percentage <= 30:
        sentence_length_score = "Orange"
    else:
        sentence_length_score = "Red"

    # 13. Keyphrase in Subheadings
    keyphrase_in_headings = sum(1 for h in headings if focus_keyword_lower in h.lower())
    kp_heading_ratio = (keyphrase_in_headings / len(headings) * 100) if len(headings) > 0 else 0
    if kp_heading_ratio >= 50:
        keyphrase_subheading_score = "Green"
    elif 20 <= kp_heading_ratio < 50:
        keyphrase_subheading_score = "Orange"
    else:
        keyphrase_subheading_score = "Red"

    # -----------------------------
    # Compile Results
    # -----------------------------
    results = {
        "Content Length": content_length_score,
        "Outbound Links": outbound_links_score,
        "Internal Links": internal_links_score,
        "Images": images_score,
        "Keyphrase in Introduction": keyphrase_intro_score,
        "Keyphrase Density": keyphrase_density_score,
        "Keyphrase Distribution": keyphrase_distribution_score,
        "Transition Words": transition_score,
        "Consecutive Sentences": consecutive_sentences_score,
        "Subheading Distribution": subheading_score,
        "Paragraph Length": paragraph_length_score,
        "Sentence Length": sentence_length_score,
        "Keyphrase in Subheadings": keyphrase_subheading_score
    }

    return results

# Example usage with the provided article_content and a focus keyword:
if __name__ == "__main__":
    article_content = """# US Demographics Reveal Surge in Herpes and Syphilis Cases Over 18 Months 
![Article Image](https://wsstgprdphotosonic01.blob.core.windows.net/photosonic/fc4b491d-3eba-4185-9be8-6c0f7fbcc4f1.png?st=2024-12-03T18%3A50%3A05Z&se=2024-12-10T18%3A50%3A05Z&sp=r&sv=2025-01-05&sr=b&sig=NwzEg8nON4dzjeysHafxMTO%2B20kml6b6sbl/jXEwkCw%3D)

<sub>Image Source: AI Generated</sub>




Recent surveillance data reveals an unprecedented 18-month surge in sexually transmitted infections across the United States, with herpes and syphilis cases reaching their highest levels since 2000. Laboratory test results from major medical centers indicate a 28% increase in herpes diagnoses and a 32% rise in syphilis cases between 2021 and 2023. This dramatic escalation represents a significant public health challenge, particularly as rising STDs affect diverse demographic groups across multiple geographic regions. The surge has created substantial pressure on healthcare systems, highlighting critical gaps in testing capacity, treatment accessibility, and preventive services. This comprehensive analysis examines the current crisis, its socioeconomic implications, and the strategic responses needed to address this growing public health concern.

## Current State of STI Crisis 


The Centers for Disease Control and Prevention's latest surveillance data indicates more than 2.4 million sexually transmitted infections were reported in the United States during 2023 <sup>[[1]](https://www.cdc.gov/media/releases/2024/p1112-sti-slowing.html)</sup>. The current state of STI transmission presents a complex public health challenge, with several infections reaching historic levels.

### Record-Breaking Infection Numbers
The total syphilis cases reached 209,253 in 2023, marking the highest number since 1950 <sup>[[2]](https://www.cdc.gov/sti-statistics/annual/summary.html)</sup>. While the overall increase has slowed to 1% compared to previous years' double-digit growth <sup>[[1]](https://www.cdc.gov/media/releases/2024/p1112-sti-slowing.html)</sup>, certain categories show concerning trends. Congenital syphilis cases rose to 3,882, including 279 stillbirths and infant deaths <sup>[[2]](https://www.cdc.gov/sti-statistics/annual/summary.html)</sup>. Notably, gonorrhea cases showed a 7% decline from 2022, dropping below pre-pandemic levels <sup>[[1]](https://www.cdc.gov/media/releases/2024/p1112-sti-slowing.html)</sup>.

### Most Affected Demographics
Significant disparities exist across population groups:

* American Indian and Alaska Native communities face the highest primary and secondary syphilis rates at 58 cases per 100,000 population <sup>[[3]](https://www.usnews.com/news/health-news/slideshows/10-states-with-the-highest-std-rates)</sup>
* Black individuals account for nearly one-third of all reported cases despite comprising only 13% of the U.S. population <sup>[[3]](https://www.usnews.com/news/health-news/slideshows/10-states-with-the-highest-std-rates)</sup>
* Nearly half of all STI cases occur among individuals aged 15-24 years <sup>[[4]](https://www.healthline.com/health-news/sti-epidemic-slows-syphilis-gonorrhea-cases-fall)</sup>

### Geographic Distribution of Cases
Regional variations reveal distinct patterns in infection rates. The South leads with 74.0 cases per 100,000 population, followed closely by the West at 75.3 cases per 100,000 <sup>[[5]](https://www.cdc.gov/sti-statistics/data-vis/table-syph-total-state-abc.html)</sup>. Several states demonstrate particularly concerning trends:

| Region | Notable Statistics |
|--------|-------------------|
| South Dakota | Highest rate increase (229.0 per 100,000) <sup>[[5]](https://www.cdc.gov/sti-statistics/data-vis/table-syph-total-state-abc.html)</sup> |
| New Mexico | 135.6 cases per 100,000 population <sup>[[5]](https://www.cdc.gov/sti-statistics/data-vis/table-syph-total-state-abc.html)</sup> |
| District of Columbia | 167.0 cases per 100,000 population <sup>[[5]](https://www.cdc.gov/sti-statistics/data-vis/table-syph-total-state-abc.html)</sup> |

The geographic distribution shows significant urban-rural disparities, with cities reporting higher testing capacity and case identification rates. However, rural areas face challenges in healthcare access and diagnosis, potentially leading to underreported cases <sup>[[6]](https://publichealth.jhu.edu/2024/why-is-syphilis-spiking-in-the-us)</sup>. This pattern suggests the need for targeted interventions and enhanced testing capabilities across diverse geographic settings.


## Healthcare System Impact 


The surge in STI cases has placed unprecedented strain on the American healthcare system, creating multifaceted challenges in testing, treatment, and resource allocation. A comprehensive analysis reveals the extent of this impact across various healthcare delivery aspects.

### Testing Capacity Challenges
The healthcare system faces significant testing constraints, with 83% of health department STI programs deferring services or field visits <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup>. Laboratory supply shortages have become particularly acute, with diagnostic test kits becoming increasingly scarce <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup>. Current testing measures remain inadequate, with many facilities using decades-old testing methodologies <sup>[[8]](https://medicine.yale.edu/news-article/how-the-stigma-of-herpes-harms-patients-and-stymies-research-for-a-cure/)</sup>. The situation is further complicated by:

* Reduced clinic hours affecting 66% of facilities
* Staff shortages impacting 62% of HIV and syphilis caseloads
* Limited laboratory supplies constraining diagnostic capabilities <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup>

### Treatment Accessibility Issues
Treatment accessibility has become increasingly problematic across different healthcare settings. More than half of state and local STI programs have experienced budget cuts, resulting in reduced clinic hours and increased patient co-pays <sup>[[9]](https://www.hhs.gov/sites/default/files/STI-National-Strategic-Plan-2021-2025.pdf)</sup>. The impact varies significantly based on insurance status and geographic location, with rural areas facing particular challenges in accessing specialized care.

### Healthcare Cost Implications
The financial burden on the healthcare system has reached unprecedented levels. Recent CDC estimates indicate that STIs impose approximately USD 16 billion in direct lifetime medical costs annually <sup>[[10]](https://www.cdc.gov/sti/php/communication-resources/prevalence-incidence-and-cost-estimates.html)</sup>. This cost burden breaks down across various aspects:

| Cost Category | Impact |
|--------------|---------|
| Direct Medical Costs | USD 15.9 billion annually <sup>[[11]](https://stacks.cdc.gov/view/cdc/135964)</sup> |
| HIV-Related Costs | USD 13.7 billion <sup>[[11]](https://stacks.cdc.gov/view/cdc/135964)</sup> |
| HPV-Related Costs | USD 0.8 billion <sup>[[11]](https://stacks.cdc.gov/view/cdc/135964)</sup> |
| Youth Impact (15-24) | USD 4.2 billion (26% of total) <sup>[[11]](https://stacks.cdc.gov/view/cdc/135964)</sup> |

The financial strain extends beyond direct medical costs, as the total burden doesn't include productivity losses, non-medical costs, and prevention program expenses <sup>[[10]](https://www.cdc.gov/sti/php/communication-resources/prevalence-incidence-and-cost-estimates.html)</sup>. Women bear a disproportionate financial burden, with lifetime costs per case of chlamydia reaching USD 360 for women compared to USD 30 for men <sup>[[12]](https://www.americanprogress.org/article/ensuring-access-to-sexually-transmitted-infection-care-for-all/)</sup>. The situation is further complicated by insurance coverage variations, with public insurance programs playing a crucial role in providing access to STI care services <sup>[[12]](https://www.americanprogress.org/article/ensuring-access-to-sexually-transmitted-infection-care-for-all/)</sup>.

The healthcare system's capacity to respond effectively has been further compromised by the COVID-19 pandemic, with STI program staff and resources being diverted to pandemic response efforts <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup>. This reallocation of resources has created additional strains on an already stressed system, potentially leading to hundreds of new HIV cases and thousands of STI cases in metropolitan areas alone <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup>.

## Socioeconomic Factors 


Socioeconomic factors play a pivotal role in shaping the landscape of sexually transmitted infections, with distinct patterns emerging across different demographic and economic groups. Analysis reveals complex interactions between social determinants and infection rates, creating significant disparities in health outcomes.

### Access to Healthcare Services
Healthcare accessibility varies dramatically across populations, with significant barriers affecting vulnerable communities. Data shows that 64% of patients accessing Title X funded services are uninsured <sup>[[12]](https://www.americanprogress.org/article/ensuring-access-to-sexually-transmitted-infection-care-for-all/)</sup>, while 24% rely on public insurance programs. Transportation limitations, language barriers, and restricted clinic hours create additional obstacles to care, particularly affecting racial and ethnic minorities <sup>[[12]](https://www.americanprogress.org/article/ensuring-access-to-sexually-transmitted-infection-care-for-all/)</sup>. In areas with limited insurance coverage, maintaining adequate healthcare resources becomes increasingly challenging, impacting even insured residents <sup>[[13]](https://pmc.ncbi.nlm.nih.gov/articles/PMC5726943/)</sup>.

### Income Level Correlations
Income levels demonstrate a strong association with STI risk patterns:

| Income Quintile | STI Diagnosis Rate |
|-----------------|-------------------|
| Poorest | 14.7% |
| Richest | 5.2% |

The poorest quintile shows 83% higher odds of STI diagnosis compared to the richest quintile <sup>[[14]](https://pmc.ncbi.nlm.nih.gov/articles/PMC3752095/)</sup>. This correlation remains consistent across racial and ethnic groups, though with varying degrees of impact. Income gradients are particularly steep among Hispanic and Black populations, with the most pronounced disparities observed among the poorest demographics <sup>[[14]](https://pmc.ncbi.nlm.nih.gov/articles/PMC3752095/)</sup>.

### Educational Awareness Gaps
Educational attainment significantly influences STI prevention and treatment outcomes. Key findings indicate:

* Individuals with less than high school education show higher infection rates for both HSV-1 and HSV-2 <sup>[[15]](https://pmc.ncbi.nlm.nih.gov/articles/PMC2921001/)</sup>
* College students demonstrate critical knowledge deficiencies about STI prevention and treatment <sup>[[16]](https://journals.sagepub.com/doi/abs/10.1177/0017896920959091)</sup>
* Provider education and awareness gaps affect the quality of sexual health conversations, particularly with younger patients <sup>[[9]](https://www.hhs.gov/sites/default/files/STI-National-Strategic-Plan-2021-2025.pdf)</sup>

The relationship between education and STI risk is compounded by other social determinants, including poverty, housing insecurity, and food instability <sup>[[9]](https://www.hhs.gov/sites/default/files/STI-National-Strategic-Plan-2021-2025.pdf)</sup>. These factors create a complex web of challenges that disproportionately affect certain communities, with social and economic conditions influencing both individual behaviors and healthcare access patterns <sup>[[17]](https://www.cdc.gov/sti/php/projects/health-equity.html)</sup>. Recent studies indicate that areas with lower educational attainment often correlate with reduced access to preventive services and higher rates of STI transmission <sup>[[12]](https://www.americanprogress.org/article/ensuring-access-to-sexually-transmitted-infection-care-for-all/)</sup>.

## Prevention Strategies 


The Centers for Disease Control and Prevention (CDC) has implemented comprehensive strategies to combat the rising tide of sexually transmitted infections, focusing on evidence-based approaches and innovative prevention methods. These initiatives represent a coordinated response to the escalating public health challenge.

### Public Health Initiatives
The CDC's Division of STD Prevention (DSTDP) leads national efforts through science-based programs and policy development <sup>[[18]](https://www.cdc.gov/nchhstp/priorities/std-prevention.html)</sup>. Their strategic approach encompasses multiple interventions, including expanded workforce knowledge and healthcare systems capacity. Recent data shows that implementing expedited partner therapy and STI partner services has resulted in a 23% improvement in treatment outcomes <sup>[[18]](https://www.cdc.gov/nchhstp/priorities/std-prevention.html)</sup>.

Key prevention initiatives include:
* Pre-exposure vaccination programs for HPV, HAV, and HBV
* Implementation of quality STI screening protocols
* Development of innovative diagnostic technologies
* Enhancement of surveillance systems

### Community Outreach Programs
Community-based prevention efforts have demonstrated significant impact through targeted interventions. The STD Surveillance Network has established comprehensive monitoring systems across various demographics <sup>[[19]](https://www.cdc.gov/sti/php/projects/index.html)</sup>. Local health departments have implemented specialized programs reaching vulnerable populations, with **57% of participants achieving successful treatment outcomes** <sup>[[20]](https://odphp.health.gov/healthypeople/objectives-and-data/browse-objectives/sexually-transmitted-infections)</sup>.

| Prevention Program | Success Rate |
|-------------------|--------------|
| Partner Services | 68% |
| Screening Programs | 73% |
| Vaccination Initiatives | 82% |

### Educational Campaigns
The CDC's educational initiatives focus on raising awareness and promoting behavioral change. The "Talk. Test. Treat." campaign has emerged as a cornerstone of prevention efforts <sup>[[21]](https://www.cdc.gov/sti-awareness/php/campaign-materials/pbyt.html)</sup>. This comprehensive approach includes:

1. Digital engagement strategies reaching 2.5 million individuals annually
2. Social media campaigns utilizing targeted messaging
3. Healthcare provider education programs
4. Community-based awareness initiatives

Recent implementation of technology-based STI partner services has shown promising results, with a **20.9% increase in testing rates** among target populations <sup>[[22]](https://www.cdc.gov/sti/prevention/index.html)</sup>. The CDC's STI Awareness Week, observed annually, has become a crucial platform for disseminating prevention information and reducing stigma <sup>[[23]](https://www.hiv.gov/blog/resources-for-sti-awareness-week-april-14-20-2024)</sup>.

These prevention strategies align with the National STI Strategic Plan, emphasizing evidence-based approaches while addressing social and structural determinants of health <sup>[[18]](https://www.cdc.gov/nchhstp/priorities/std-prevention.html)</sup>. Through coordinated efforts between federal, state, and local agencies, these initiatives work to reverse the current trends in STI rates while ensuring equitable access to prevention services.


## Future Projections 


Analysis of current epidemiological data suggests significant shifts in sexually transmitted infection patterns across the United States, with projections indicating evolving challenges for public health systems.

### Expected Trend Analysis
Recent surveillance data indicates promising developments in certain areas, with gonorrhea cases dropping 7% from 2022 levels <sup>[[1]](https://www.cdc.gov/media/releases/2024/p1112-sti-slowing.html)</sup>. Primary and secondary syphilis cases have declined for the first time in over two decades, showing a 10% reduction since 2022 <sup>[[1]](https://www.cdc.gov/media/releases/2024/p1112-sti-slowing.html)</sup>. Among gay and bisexual men, a notable 13% decrease marks the first decline since CDC began tracking national trends for this demographic group <sup>[[1]](https://www.cdc.gov/media/releases/2024/p1112-sti-slowing.html)</sup>.

However, concerning patterns persist:
* Congenital syphilis cases continue rising, albeit at a slower 3% rate compared to previous 30% annual increases <sup>[[1]](https://www.cdc.gov/media/releases/2024/p1112-sti-slowing.html)</sup>
* Overall syphilis cases increased by 1% after years of double-digit growth <sup>[[1]](https://www.cdc.gov/media/releases/2024/p1112-sti-slowing.html)</sup>
* Testing capacity remains significantly impacted by COVID-19 disruptions <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup>

### Healthcare System Preparedness
The healthcare infrastructure faces substantial challenges in managing future STI cases. Current data reveals that 83% of health department STI programs are deferring services or field visits <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup>. A comprehensive analysis of testing capabilities shows:

| Service Area | Impact Level |
|--------------|--------------|
| STI Screening | 66% decrease in capacity <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup> |
| HIV/Syphilis Cases | 62% unable to maintain caseload <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup> |
| Laboratory Supplies | Significant shortages reported <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup> |

These challenges are compounded by the diversion of STI program staff to COVID-19 response efforts, potentially leading to hundreds of new HIV cases and thousands of STI cases in metropolitan areas alone <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup>.

### Resource Allocation Needs
**Critical funding requirements** have emerged as more than half of state and local STI programs face budget constraints, resulting in reduced clinic hours and increased patient costs <sup>[[9]](https://www.hhs.gov/sites/default/files/STI-National-Strategic-Plan-2021-2025.pdf)</sup>. The situation demands strategic resource allocation across multiple domains:

The implementation of modernized surveillance systems requires substantial investment, as highlighted by the National Association of Public Health Officials <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup>. Current projections indicate a need for enhanced testing capabilities and expanded laboratory infrastructure to address future case volumes effectively <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup>.

Healthcare facilities must prepare for increased demand while managing resource constraints. This includes addressing the shortage of STI diagnostic test kits and laboratory supplies <sup>[[7]](https://www.ncbi.nlm.nih.gov/books/NBK573147/)</sup>, which has been exacerbated by competing demands from COVID-19 testing requirements.

The development of innovative prevention tools, including post-exposure prophylaxis and improved diagnostic tests, represents a critical area for resource investment <sup>[[24]](https://www.npr.org/2024/01/31/1228195107/syphilis-cases-soar-in-us-cdc-says)</sup>. These advancements will require coordinated efforts at federal, state, and local levels to ensure effective implementation and accessibility <sup>[[24]](https://www.npr.org/2024/01/31/1228195107/syphilis-cases-soar-in-us-cdc-says)</sup>.

**Future preparedness initiatives** must focus on strengthening the STI infrastructure and expanding the workforce, offering dual benefits of improved STI control and enhanced readiness for future public health threats <sup>[[25]](https://www.nationalacademies.org/our-work/prevention-and-control-of-sexually-transmitted-infections-in-the-united-states)</sup>. This approach requires sustained funding commitments and strategic resource allocation to address both immediate needs and long-term prevention goals.


## Conclusion 


Recent data paints a clear picture of America's growing STI crisis, marked by record-breaking infection rates and strained healthcare resources. Statistical evidence demonstrates significant disparities across demographic groups, with marginalized communities bearing a disproportionate burden of new infections. Healthcare systems face mounting pressure from reduced testing capacity, limited resources, and budget constraints, while annual costs exceed USD 16 billion in direct medical expenses alone.

Prevention strategies show promise through targeted interventions and community outreach programs, though significant challenges remain. Success rates above 70% in screening and vaccination initiatives demonstrate effective approaches when properly implemented and resourced. Future projections suggest mixed trends, with some infections showing decline while others, particularly congenital syphilis, continue to rise.

Strategic action requires sustained funding commitments, enhanced testing capabilities, and strengthened public health infrastructure. Success depends on addressing both immediate healthcare needs and underlying socioeconomic factors that drive infection rates. Public health officials, healthcare providers, and community organizations must unite to combat this escalating crisis through evidence-based approaches and equitable resource distribution.

## References 
[1] - https://www.cdc.gov/media/releases/2024/p1112-sti-slowing.html  
[2] - https://www.cdc.gov/sti-statistics/annual/summary.html  
[3] - https://www.usnews.com/news/health-news/slideshows/10-states-with-the-highest-std-rates  
[4] - https://www.healthline.com/health-news/sti-epidemic-slows-syphilis-gonorrhea-cases-fall  
[5] - https://www.cdc.gov/sti-statistics/data-vis/table-syph-total-state-abc.html  
[6] - https://publichealth.jhu.edu/2024/why-is-syphilis-spiking-in-the-us  
[7] - https://www.ncbi.nlm.nih.gov/books/NBK573147/  
[8] - https://medicine.yale.edu/news-article/how-the-stigma-of-herpes-harms-patients-and-stymies-research-for-a-cure/  
[9] - https://www.hhs.gov/sites/default/files/STI-National-Strategic-Plan-2021-2025.pdf  
[10] - https://www.cdc.gov/sti/php/communication-resources/prevalence-incidence-and-cost-estimates.html  
[11] - https://stacks.cdc.gov/view/cdc/135964  
[12] - https://www.americanprogress.org/article/ensuring-access-to-sexually-transmitted-infection-care-for-all/  
[13] - https://pmc.ncbi.nlm.nih.gov/articles/PMC5726943/  
[14] - https://pmc.ncbi.nlm.nih.gov/articles/PMC3752095/  
[15] - https://pmc.ncbi.nlm.nih.gov/articles/PMC2921001/  
[16] - https://journals.sagepub.com/doi/abs/10.1177/0017896920959091  
[17] - https://www.cdc.gov/sti/php/projects/health-equity.html  
[18] - https://www.cdc.gov/nchhstp/priorities/std-prevention.html  
[19] - https://www.cdc.gov/sti/php/projects/index.html  
[20] - https://odphp.health.gov/healthypeople/objectives-and-data/browse-objectives/sexually-transmitted-infections  
[21] - https://www.cdc.gov/sti-awareness/php/campaign-materials/pbyt.html  
[22] - https://www.cdc.gov/sti/prevention/index.html  
[23] - https://www.hiv.gov/blog/resources-for-sti-awareness-week-april-14-20-2024  
[24] - https://www.npr.org/2024/01/31/1228195107/syphilis-cases-soar-in-us-cdc-says  
[25] - https://www.nationalacademies.org/our-work/prevention-and-control-of-sexually-transmitted-infections-in-the-united-states"""

    focus_keyword = "herpes and syphilis"
    scores = evaluate_article(article_content, focus_keyword)
    print("SEO Evaluation Results:")
    for criterion, score in scores.items():
        print(f"{criterion}: {score}")
