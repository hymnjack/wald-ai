import os
import openai
import sys
from pathlib import Path
import dotenv

# Load environment variables from .env file in the agents/yoast_seo directory
dotenv_path = Path(os.path.dirname(__file__)).parent / '.env'
dotenv.load_dotenv(dotenv_path)

def generate_correction(user_input, focus_keyword, yoast_results):
    """
    Generate content improvement suggestions using OpenAI's o3-mini model based on Yoast SEO evaluation results.
    
    Args:
        user_input (str): The original content provided by the user
        yoast_results (dict): The evaluation results from Yoast SEO
    
    Returns:
        str: Rewritten content that improves on the evaluation scores
    """
    # Set up OpenAI client
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    if not openai.api_key:
        return "Error: OPENAI_API_KEY environment variable not set. Please set your API key."
    
    # Create a summary of the Yoast evaluation results
    results_summary = []
    for criterion, score in yoast_results.items():
        results_summary.append(f"- {criterion}: {score}")
    
    results_text = "\n".join(results_summary)
    
    # Create the system prompt with Yoast SEO evaluation criteria
    system_prompt = f"""You are an expert SEO content optimizer. Your task is to REWRITE the provided content to improve its SEO performance based on Yoast SEO evaluation results.

Here's how Yoast SEO evaluates content:

1. Content Length:
   - Green: Content exceeds 900 words
   - Orange: Content is between 600-900 words
   - Red: Content is less than 600 words

2. Outbound Links:
   - Green: At least one outbound/external link
   - Red: No outbound/external links

3. Internal Links:
   - Green: At least one internal link
   - Red: No internal links

4. Images:
   - Green: At least one image
   - Red: No images

5. Keyphrase in Introduction:
   - Green: Keyphrase in the first sentence of introduction
   - Red: Keyphrase not in first sentence

6. Keyphrase Density:
   - Green: 0.5% to 2.5%
   - Orange: 2.5% to 3%
   - Red: Less than 0.5% or more than 3%

7. Keyphrase Distribution:
   - Green: Evenly distributed (~1 per 100-150 words)
   - Orange: Uneven distribution
   - Red: Poor distribution (<4 occurrences in 1000 words)

8. Transition Words:
   - Green: 30%+ sentences contain transition words
   - Orange: 20-30% sentences contain transition words
   - Red: <20% sentences contain transition words

9. Consecutive Sentences:
   - Green: No 3+ consecutive sentences start with same word
   - Orange: Multiple instances of 2 consecutive sentences start with same word
   - Red: 3+ consecutive sentences start with same word

10. Subheading Distribution:
    - Green: All sections ≤300 words between subheadings
    - Orange: At least one section >300 words without subheading
    - Red: Multiple sections >300 words without subheadings

11. Paragraph Length:
    - Green: <150 words and >2 sentences
    - Orange: 150-200 words
    - Red: >200 words or <2 sentences

12. Sentence Length:
    - Green: ≤25% sentences longer than 20 words
    - Orange: 25-30% sentences longer than 20 words
    - Red: >30% sentences longer than 20 words

13. Keyphrase in Subheadings:
    - Green: Keyphrase in ≥50% of headings
    - Orange: Keyphrase in 20-50% of headings
    - Red: Keyphrase in <20% of headings

You must COMPLETELY REWRITE the content to improve the SEO scores, focusing especially on areas marked as Red or Orange. Maintain the original meaning and information, but optimize the content structure and wording to achieve better Yoast SEO scores."""
    
    # Create the user prompt
    user_prompt = f"""Here is the content to improve:

{user_input}

Focus Keyphrase: {focus_keyword}

Here are the Yoast SEO evaluation results:

{results_text}

Please COMPLETELY REWRITE this content to improve its SEO performance based on the Yoast SEO evaluation results above. Focus on fixing the issues marked as Red or Orange first. Maintain the original meaning and information, but optimize the structure and wording to achieve better scores.

Make sure to properly incorporate the focus keyphrase "{focus_keyword}" throughout the content according to the Yoast SEO guidelines.

Your response should be the fully rewritten content ready to be used, not just suggestions.

REWRITTEN CONTENT:"""
    
    # Call the OpenAI API with o3-mini model
    try:
        response = openai.chat.completions.create(
            model="o3-mini",  # Using OpenAI's o3-mini model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            return "Error: Unable to generate rewritten content. Please try again."
    
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Test the function
    test_input = "This is a test article about SEO. It's very short and doesn't have any links or images."
    test_focus_keyword = "SEO"
    test_results = {
        "Content Length": "Red",
        "Outbound Links": "Red",
        "Internal Links": "Red",
        "Images": "Red",
        "Keyphrase in Introduction": "Green",
        "Keyphrase Density": "Orange"
    }
    
    print(generate_correction(test_input, test_focus_keyword, test_results))
