import re
import requests
import torch
import time
import random

# Hugging Face API token and URLs
API_TOKEN = "token"
QG_API_URL = "https://api-inference.huggingface.co/models/valhalla/t5-small-qg-hl"
QA_API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
SBERT_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# 1. Input context (your original context here)
context = """
The conversion of usable sunlight energy into chemical energy is associated with the action of the green pigment chlorophyll. Chlorophyll is a complex molecule. Several modifications of chlorophyll occur among plants and other photosynthetic organisms. All photosynthetic organisms have chlorophyll a. Accessory pigments absorb energy that chlorophyll a does not absorb. Accessory pigments include chlorophyll b (also c, d, and e in algae and protistans), xanthophylls, and carotenoids (such as beta-carotene). Chlorophyll a absorbs its energy from the violet-blue and reddish orange-red wavelengths, and little from the intermediate (green-yellow-orange) wavelengths. Chlorophyll All chlorophylls have: • a lipid-soluble hydrocarbon tail (C20H39 -) • a flat hydrophilic head with a magnesium ion at its centre; different chlorophylls have different side-groups on the head The tail and head are linked by an ester bond. Leaves and leaf structure Plants are the only photosynthetic organisms to have leaves (and not all plants have leaves). A leaf may be viewed as a solar collector crammed full of photosynthetic cells. The raw materials of photosynthesis, water and carbon dioxide, enter the cells of the leaf, and the products of photosynthesis, sugar and oxygen, leave the leaf. Water enters the root and is transported up to the leaves through specialized plant cells known as xylem vessels. Land plants must guard against drying out and so have evolved specialized structures known as stomata to allow gas to enter and leave the leaf. Carbon dioxide cannot pass through the protective waxy layer covering the leaf (cuticle), but it can enter the leaf through the stoma (the singular of stomata), flanked by two guard cells. Likewise, oxygen produced during photosynthesis can only pass out of the leaf through the opened stomata. Unfortunately for the plant, while these gases are moving between the inside and outside of the leaf, a great deal of water is also lost. Cottonwood trees, for example, will lose 100 gallons (about 450 dm3) of water per hour during hot desert days. The structure of the chloroplast and photosynthetic membranes The thylakoid is the structural unit of photosynthesis. Both photosynthetic prokaryotes and eukaryotes have these flattened sacs/vesicles containing photosynthetic chemicals. Only eukaryotes have chloroplasts with a surrounding membrane. Thylakoids are stacked like pancakes in stacks known collectively as grana. The areas between grana are referred to as stroma. While the mitochondrion has two membrane systems, the chloroplast has three, forming three compartments. Stages of photosynthesis When chlorophyll a absorbs light energy, an electron gains energy and is 'excited'. The excited electron is transferred to another molecule (called a primary electron acceptor). The chlorophyll molecule is oxidized (loss of electron) and has a positive charge. Photoactivation of chlorophyll a results in the splitting of water molecules and the transfer of energy to ATP and reduced nicotinamide adenine dinucleotide phosphate (NADP). The chemical reactions involved include: • condensation reactions - responsible for water molecules splitting out, including phosphorylation (the addition of a phosphate group to an organic compound) • oxidation/reduction (redox) reactions involving electron transfer Photosynthesis is a two stage process. The light dependent reactions, a light-dependent series of reactions which occur in the grana, and require the direct energy of light to make energy-carrier molecules that are used in the second process: • light energy is trapped by chlorophyll to make ATP (photophosphorylation) • at the same time water is split into oxygen, hydrogen ions and free electrons: 2H2O    4H+ + O2 + 4e- (photolysis) • the electrons then react with a carrier molecule nicotinamide adenine dinucleotide phosphate (NADP), changing it from its oxidised state (NADP+) to its reduced state (NADPH): NADP+ + 2e- + 2H+    NADPH + H+ The light-independent reactions, a light-independent series of reactions which occur in the stroma of the chloroplasts, when the products of the light reaction, ATP and NADPH, are used to make carbohydrates from carbon dioxide (reduction); initially glyceraldehyde 3-phosphate (a 3-carbon atom molecule) is formed. """

# 2. Improved function to generate questions
def generate_questions(context, target_question_count=15):
    # Clean up the context
    clean_context = context.replace("\n\n", " ").strip()
    
    # Extract major sections to create more meaningful chunks
    sections = []
    
    # First try to extract sections by headings
    main_sections = re.split(r'(?:\n|^)(.*?):?\n', clean_context)
    
    current_section = ""
    for i, part in enumerate(main_sections):
        if i % 2 == 0:  # Even indices contain content
            current_section += part + " "
        else:  # Odd indices might contain headings
            if part.strip() and len(part.strip()) < 100:  # Likely a heading
                if current_section.strip():
                    sections.append(current_section.strip())
                current_section = part + ": "
            else:
                current_section += part + " "
    
    if current_section.strip():
        sections.append(current_section.strip())
    
    # If we couldn't extract good sections, fall back to paragraph-based chunking
    if len(sections) < 3:
        # Split by paragraphs
        sections = [p.strip() for p in re.split(r'\n\s*\n', clean_context) if p.strip()]
    
    # Further ensure we have a reasonable number of sections
    if len(sections) < 3:
        # Create chunks by sentences
        sentences = re.split(r'(?<=[.!?])\s+', clean_context)
        sections = []
        chunk = ""
        
        for sentence in sentences:
            if len(chunk) + len(sentence) < 800:  # Increased chunk size for better context
                chunk += sentence + " "
            else:
                if chunk.strip():
                    sections.append(chunk.strip())
                chunk = sentence + " "
        
        if chunk.strip():
            sections.append(chunk.strip())
    
    # Ensure sections are substantial
    sections = [s for s in sections if len(s) > 100]
    
    if not sections:
        print("ERROR: Could not extract meaningful sections from the text.")
        return []
    
    # Distribute sections evenly to get close to target_question_count
    section_count = min(len(sections), max(3, target_question_count // 2))
    
    # Choose sections evenly distributed throughout the document
    step = max(1, len(sections) // section_count)
    selected_sections = [sections[i] for i in range(0, len(sections), step)][:section_count]
    
    # Add intro and conclusion if available and not already included
    if len(sections) >= 3 and sections[0] not in selected_sections:
        selected_sections.insert(0, sections[0])
    if len(sections) >= 4 and sections[-1] not in selected_sections:
        selected_sections.append(sections[-1])
    
    all_questions = []
    used_questions = set()  # Track unique questions
    
    # Generate questions for each selected section
    for section in selected_sections:
        # Clean up the section to make it more coherent
        clean_section = re.sub(r'\s+', ' ', section).strip()
        
        prompt = f"generate questions: {clean_section}"
        payload = {"inputs": prompt}
        
        try:
            response = requests.post(QG_API_URL, headers=headers, json=payload)
            print(f"API response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    raw_text = result[0]["generated_text"]
                    
                    # Parse questions, ensuring they end with question marks
                    section_questions = []
                    for q in raw_text.split("\n"):
                        q = q.strip()
                        if q and not q.endswith("?"):
                            q += "?"
                        
                        # Only add meaningful, non-duplicate questions
                        normalized_q = q.lower()
                        if q and len(q) > 10 and normalized_q not in used_questions:
                            section_questions.append(q)
                            used_questions.add(normalized_q)
                    
                    # Get top 2-3 questions per section for variety
                    section_questions = section_questions[:3]
                    
                    print(f"Generated questions: {section_questions}")
                    all_questions.extend(section_questions)
            
            # Backoff delay for API rate limits
            time.sleep(2)
            
        except Exception as e:
            print(f"Error generating questions: {e}")
    
    # If we still don't have enough questions, try with larger chunks of the text
    if len(all_questions) < target_question_count // 2:
        try:
            # Use the first half of the document as one chunk
            half_doc = ' '.join(sections[:len(sections)//2])
            prompt = f"generate questions: {half_doc[:1500]}"  # Limit to avoid API issues
            payload = {"inputs": prompt}
            
            response = requests.post(QG_API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    raw_text = result[0]["generated_text"]
                    
                    for q in raw_text.split("\n"):
                        q = q.strip()
                        if q and not q.endswith("?"):
                            q += "?"
                        
                        normalized_q = q.lower()
                        if q and len(q) > 10 and normalized_q not in used_questions:
                            all_questions.append(q)
                            used_questions.add(normalized_q)
            
            time.sleep(2)
        except Exception as e:
            print(f"Error in backup question generation: {e}")
    
    # Final check for quality
    filtered_questions = []
    for q in all_questions:
        # Skip questions about layout or presentation
        if re.search(r'page|bullet|number|list|heading', q.lower()):
            continue
        # Skip generic questions
        if q.lower() in ['what is this?', 'what is the main idea?', 'what is the topic?']:
            continue
        # Add good questions
        filtered_questions.append(q)
    
    # Remove duplicates while preserving order
    unique_questions = []
    seen = set()
    for q in filtered_questions:
        q_lower = q.lower().strip()
        if q_lower not in seen and len(q) > 10:
            unique_questions.append(q)
            seen.add(q_lower)
    
    # Limit to target question count
    return unique_questions[:target_question_count]

# 3. Improved answer extraction
def get_answer(context, question):
    # Clean the context to remove formatting issues
    clean_context = re.sub(r'\s+', ' ', context).strip()
    
    payload = {
        "inputs": {
            "question": question,
            "context": clean_context
        }
    }
    
    try:
        response = requests.post(QA_API_URL, headers=headers, json=payload)
        time.sleep(1)  # Rate limiting

        if response.status_code == 200:
            answer_data = response.json()
            raw_answer = answer_data.get("answer", "").strip()
            
            # Validate answer quality
            if not raw_answer or len(raw_answer) < 3 or raw_answer.isdigit():
                # Try with a smaller context that's more targeted
                relevant_paragraphs = []
                paragraphs = re.split(r'\n\s*\n', context)
                
                for para in paragraphs:
                    # Find paragraphs that might contain the answer
                    if any(word in para.lower() for word in question.lower().split() if len(word) > 3):
                        relevant_paragraphs.append(para)
                
                if relevant_paragraphs:
                    targeted_context = ' '.join(relevant_paragraphs)
                    payload["inputs"]["context"] = targeted_context
                    
                    response = requests.post(QA_API_URL, headers=headers, json=payload)
                    time.sleep(1)
                    
                    if response.status_code == 200:
                        answer_data = response.json()
                        improved_answer = answer_data.get("answer", "").strip()
                        
                        if len(improved_answer) > len(raw_answer):
                            raw_answer = improved_answer
            
            # Clean the answer
            clean_answer = re.sub(r'\s+', ' ', raw_answer).strip()
            return clean_answer
        else:
            print(f"QA API Error: {response.status_code} - {response.text}")
            return ""
    except Exception as e:
        print(f"Error getting answer: {e}")
        return ""

# 4. Get sentence embedding from SBERT API
def get_embedding(text):
    # Clean and validate text
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return None
    
    try:
        response = requests.post(SBERT_API_URL, headers=headers, json={"inputs": text})
        time.sleep(1)
        
        if response.status_code == 200:
            return torch.tensor(response.json()[0])
        else:
            print(f"SBERT API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

# 5. Cosine similarity (unchanged)
def cosine_similarity(vec1, vec2):
    # Flatten both tensors to ensure they're compatible
    vec1_flat = vec1.flatten()
    vec2_flat = vec2.flatten()
    
    # Calculate dot product
    dot_product = torch.dot(vec1_flat, vec2_flat)
    
    # Calculate magnitudes
    magnitude1 = torch.norm(vec1_flat)
    magnitude2 = torch.norm(vec2_flat)
    
    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    # Return cosine similarity
    return (dot_product / (magnitude1 * magnitude2)).item()


# NEW: Extract key phrases from content
def extract_key_phrases(context):
    """Extract complete phrases that could serve as good distractors"""
    key_phrases = []
    
    # Extract definitions and complete statements
    lines = context.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for definition patterns (X: Y or X is Y)
        if ': ' in line and len(line) < 200:
            parts = line.split(': ', 1)
            if len(parts) == 2 and len(parts[1]) > 10:
                key_phrases.append(parts[1].strip())
        
        # Look for sentences that define concepts
        if re.search(r'^\s*[•-]\s+\w+:', line):
            match = re.search(r'[•-]\s+(\w+):\s*(.+)', line)
            if match and len(match.group(2)) > 10:
                key_phrases.append(match.group(2).strip())
        
        # Look for numbered items with definitions
        if re.search(r'^\s*\d+\.\s+\w+:', line):
            match = re.search(r'\d+\.\s+(\w+):\s*(.+)', line)
            if match and len(match.group(2)) > 10:
                key_phrases.append(match.group(2).strip())
    
    # Extract complete sentences from paragraphs
    paragraphs = re.split(r'\n\s*\n', context)
    for para in paragraphs:
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', para)
        for sentence in sentences:
            # Only include complete, meaningful sentences
            clean_sentence = re.sub(r'\s+', ' ', sentence).strip()
            if (clean_sentence.endswith('.') or clean_sentence.endswith('!') or clean_sentence.endswith('?')) and \
               len(clean_sentence) > 30 and len(clean_sentence) < 150:
                key_phrases.append(clean_sentence)
    
    # Clean and deduplicate
    cleaned_phrases = []
    seen = set()
    for phrase in key_phrases:
        clean_phrase = re.sub(r'\s+', ' ', phrase).strip()
        if clean_phrase and clean_phrase.lower() not in seen:
            cleaned_phrases.append(clean_phrase)
            seen.add(clean_phrase.lower())
    
    return cleaned_phrases

# Extract key concepts from context
def extract_concepts(context):
    """Extract key concepts that can be used to generate plausible distractors"""
    concepts = []
    
    # Look for bold or emphasized terms
    for line in context.split('\n'):
        # Look for terms followed by colon or before "is/are" statements
        matches = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):', line)
        concepts.extend(matches)
        
        matches = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:is|are)', line)
        concepts.extend(matches)
    
    # Extract terms from bullet points
    for line in context.split('\n'):
        if re.search(r'^\s*[•-]\s+(\w+):', line):
            match = re.search(r'[•-]\s+(\w+):', line)
            if match:
                concepts.append(match.group(1))
    
    # Clean and deduplicate
    cleaned_concepts = []
    seen = set()
    for concept in concepts:
        clean_concept = concept.strip()
        if clean_concept and clean_concept.lower() not in seen:
            cleaned_concepts.append(clean_concept)
            seen.add(clean_concept.lower())
    
    return cleaned_concepts

# IMPROVED: Generate contextually appropriate distractors
def generate_distractors(answer, question, context, top_k=3):
    """Generate distractors that are complete, grammatically correct, and contextually appropriate"""
    
    # Clean the answer and question for analysis
    clean_answer = re.sub(r'\s+', ' ', answer).strip()
    clean_question = re.sub(r'\s+', ' ', question).strip()
    
    # Determine the question type to generate appropriate distractors
    question_type = analyze_question_type(clean_question)
    
    # Extract key phrases from context for potential distractors
    key_phrases = extract_key_phrases(context)
    
    # Extract key concepts for generating distractors
    concepts = extract_concepts(context)
    
    # Different strategies based on question type
    if question_type == "what_is":
        # For definition questions, use other definitions from the text
        return generate_definition_distractors(clean_answer, clean_question, key_phrases, top_k)
    
    elif question_type == "what_are":
        # For "what are X" questions, find other comparable lists or concepts
        return generate_list_distractors(clean_answer, clean_question, key_phrases, concepts, top_k)
    
    elif question_type == "how_to":
        # For process questions, find other process descriptions
        return generate_process_distractors(clean_answer, clean_question, key_phrases, top_k)
    
    elif question_type == "why":
        # For explanation questions, find other explanations
        return generate_explanation_distractors(clean_answer, clean_question, key_phrases, top_k)
    
    else:
        # Default strategy using semantic similarity
        return generate_semantic_distractors(clean_answer, clean_question, key_phrases, top_k)

# Analyze the question type
def analyze_question_type(question):
    """Determine the type of question to generate appropriate distractors"""
    question_lower = question.lower()
    
    if re.search(r'^what\s+is\s+', question_lower):
        return "what_is"
    elif re.search(r'^what\s+are\s+', question_lower):
        return "what_are"
    elif re.search(r'^how\s+to\s+|^how\s+do\s+|^how\s+does\s+', question_lower):
        return "how_to"
    elif re.search(r'^why\s+', question_lower):
        return "why"
    else:
        return "general"

# Generate definition distractors
def generate_definition_distractors(answer, question, key_phrases, top_k=3):
    """Generate distractors for 'what is' questions"""
    answer_lower = answer.lower()
    
    # Extract the subject of the question
    subject_match = re.search(r'what\s+is\s+(.*?)\??$', question.lower())
    subject = subject_match.group(1) if subject_match else ""
    
    # Find definition-style statements that don't contain the answer
    definition_distractors = []
    for phrase in key_phrases:
        phrase_lower = phrase.lower()
        # Skip if too similar to the answer
        if phrase_lower == answer_lower or (len(phrase_lower) > 5 and (phrase_lower in answer_lower or answer_lower in phrase_lower)):
            continue
        
        # Check if it's a complete definition
        if re.search(r'^[A-Za-z].*[.!?]$', phrase) and len(phrase) > 20:
            definition_distractors.append(phrase)
    
    # If we don't have enough, generate some based on key concepts
    if len(definition_distractors) < top_k:
        # Extract subjects/objects from the text
        chunks = re.findall(r'([A-Za-z]+(?:\s+[A-Za-z]+){1,5})\s+(?:is|refers to|means|defines|represents)\s+([^.!?;]+)', ' '.join(key_phrases))
        
        for obj, definition in chunks:
            if obj.lower() != subject and definition.lower() != answer_lower:
                # Make sure it's a complete phrase
                if not definition.endswith('.'):
                    definition = definition.strip() + '.'
                
                definition_distractors.append(definition)
    
    # Sort by length to prefer more complete definitions
    definition_distractors.sort(key=len, reverse=True)
    
    # Select the top K distractors
    selected_distractors = []
    seen = set()
    
    for distractor in definition_distractors:
        clean_distractor = re.sub(r'\s+', ' ', distractor).strip()
        if clean_distractor.lower() not in seen and len(clean_distractor) > 10:
            selected_distractors.append(clean_distractor)
            seen.add(clean_distractor.lower())
        
        if len(selected_distractors) >= top_k:
            break
    
    
    
    return selected_distractors

# Generate list distractors
def generate_list_distractors(answer, question, key_phrases, concepts, top_k=3):
    """Generate distractors for 'what are' questions"""
    answer_lower = answer.lower()
    
    # Look for lists and enumerations in the text
    list_distractors = []
    
    # Find sentences with "such as" or containing lists
    for phrase in key_phrases:
        if re.search(r'such as|include[s]?|consist[s]? of|example[s]?', phrase.lower()) and phrase.lower() != answer_lower:
            list_distractors.append(phrase)
    
    # Find sentences with commas and "and/or"
    for phrase in key_phrases:
        if re.search(r',.*(?:and|or)', phrase.lower()) and phrase.lower() != answer_lower:
            list_distractors.append(phrase)
    
    # Generate distractors using concepts
    if len(list_distractors) < top_k and concepts:
        # Use pairs of concepts to create distractors
        for i in range(len(concepts)):
            for j in range(i+1, min(i+4, len(concepts))):
                distractor = f"{concepts[i]} and {concepts[j]} working together"
                if distractor.lower() != answer_lower:
                    list_distractors.append(distractor)
    
    # Clean and deduplicate
    selected_distractors = []
    seen = set()
    
    for distractor in list_distractors:
        clean_distractor = re.sub(r'\s+', ' ', distractor).strip()
        if clean_distractor.lower() not in seen and len(clean_distractor) > 10:
            selected_distractors.append(clean_distractor)
            seen.add(clean_distractor.lower())
        
        if len(selected_distractors) >= top_k:
            break
    
    
    return selected_distractors

# Generate process distractors
def generate_process_distractors(answer, question, key_phrases, top_k=3):
    """Generate distractors for 'how to' questions"""
    answer_lower = answer.lower()
    
    # Look for process descriptions
    process_distractors = []
    
    for phrase in key_phrases:
        if phrase.lower() != answer_lower and re.search(r'by\s+|through\s+|using\s+|with\s+', phrase.lower()):
            process_distractors.append(phrase)
    
    # Clean and deduplicate
    selected_distractors = []
    seen = set()
    
    for distractor in process_distractors:
        clean_distractor = re.sub(r'\s+', ' ', distractor).strip()
        if clean_distractor.lower() not in seen and len(clean_distractor) > 10:
            selected_distractors.append(clean_distractor)
            seen.add(clean_distractor.lower())
        
        if len(selected_distractors) >= top_k:
            break
    
    return selected_distractors

# Generate explanation distractors
def generate_explanation_distractors(answer, question, key_phrases, top_k=3):
    """Generate distractors for 'why' questions"""
    answer_lower = answer.lower()
    
    # Look for explanations
    explanation_distractors = []
    
    for phrase in key_phrases:
        if phrase.lower() != answer_lower and re.search(r'because\s+|due to\s+|as a result of\s+|in order to\s+', phrase.lower()):
            explanation_distractors.append(phrase)
    
    # Clean and deduplicate
    selected_distractors = []
    seen = set()
    
    for distractor in explanation_distractors:
        clean_distractor = re.sub(r'\s+', ' ', distractor).strip()
        if clean_distractor.lower() not in seen and len(clean_distractor) > 10:
            selected_distractors.append(clean_distractor)
            seen.add(clean_distractor.lower())
        
        if len(selected_distractors) >= top_k:
            break
    
    return selected_distractors

# Generate semantic distractors
def generate_semantic_distractors(answer, question, key_phrases, top_k=3):
    """Generate distractors based on semantic similarity"""
    answer_lower = answer.lower()
    
    # Get embedding of the answer
    answer_emb = get_embedding(answer)
    if answer_emb is None:
        # Fall back to alternative method if embedding fails
        return []
    
    # Calculate similarity for each phrase
    scored_phrases = []
    for phrase in key_phrases:
        if phrase.lower() != answer_lower:
            phrase_emb = get_embedding(phrase)
            if phrase_emb is not None:
                similarity = cosine_similarity(answer_emb, phrase_emb)
                # We want related but different content - aim for mid-range similarity
                sweet_spot = abs(similarity - 0.5)  # Closer to 0.5 similarity is ideal
                scored_phrases.append((phrase, sweet_spot))
    
    # Sort by the "sweet spot" score (lower is better)
    scored_phrases.sort(key=lambda x: x[1])
    
    # Get the top phrases
    best_phrases = [p for p, _ in scored_phrases[:top_k*2]]
    
    # Clean and extract meaningful segments
    selected_distractors = []
    seen = set()
    
    for phrase in best_phrases:
        # Clean the phrase
        clean_phrase = re.sub(r'\s+', ' ', phrase).strip()
        
        # Extract a manageable segment if it's too long
        if len(clean_phrase) > 120:
            sentences = re.split(r'(?<=[.!?])\s+', clean_phrase)
            if sentences:
                clean_phrase = sentences[0].strip()
        
        # Ensure it's not too similar to the answer
        if clean_phrase.lower() not in seen and clean_phrase.lower() != answer_lower and len(clean_phrase) > 10:
            selected_distractors.append(clean_phrase)
            seen.add(clean_phrase.lower())
        
        if len(selected_distractors) >= top_k:
            break
    
    return selected_distractors



# Create quiz with improved distractor generation
def create_quiz(context, target_question_count=9):
    print("\nStarting improved quiz generation...")
    print("Generating questions...")
    
    questions = generate_questions(context, target_question_count)
    
    if not questions:
        print("ERROR: Quiz generation failed. No questions were generated.")
        return []
    
    print(f"Processing {len(questions)} questions...")
    
    quiz = []
    used_answers = set()  # Track unique answers
    
    for question in questions:
        # Get and validate answer
        answer = get_answer(context, question)
        
        # Skip if answer is missing, too short, or a single number
        if not answer or len(answer) < 5 or answer.isdigit():
            print(f"Skipping question with poor answer: {question} -> {answer}")
            continue
        
        # Clean the answer
        clean_answer = re.sub(r'\s+', ' ', answer).strip()
        answer_lower = clean_answer.lower()
        
        # Skip duplicate answers
        if answer_lower in used_answers:
            print(f"Skipping question with duplicate answer: {question}")
            continue
        
        # Generate and validate distractors
        distractors = generate_distractors(clean_answer, question, context)
        
        # Skip if we couldn't generate good distractors
        if len(distractors) < 2:
            print(f"Skipping question with insufficient distractors: {question}")
            continue
        
        quiz.append({
            "question": question,
            "answer": clean_answer,
            "distractors": distractors
        })
        
        used_answers.add(answer_lower)
        
        # Break if we have enough questions
        if len(quiz) >= target_question_count:
            break
        
        time.sleep(1)  # Rate limiting
    
    return quiz

# Format the quiz in JavaScript format
def format_javascript_quiz(quiz):
    if not quiz:
        return "const quiz = [];"
    
    js_output = "const quiz = [\n"
    
    for item in quiz:
        js_output += "  {\n"
        js_output += f'    question: "{item["question"]}",\n'
        js_output += f'    answer: "{item["answer"]}",\n'
        
        # Create and shuffle options (answer + distractors)
        options = [item["answer"]] + item["distractors"]
        random.shuffle(options)
        
        js_output += "    options: [\n"
        for option in options:
            js_output += f'      "{option}",\n'
        js_output += "    ]\n"
        js_output += "  },\n"
    
    js_output += "];"
    return js_output

# Main execution
if __name__ == "__main__":
    # Get essential functions from the original code
    
    TARGET_QUESTION_COUNT = 9
    
    # Create the quiz
    quiz = create_quiz(context, TARGET_QUESTION_COUNT)
    
    if not quiz:
        print("ERROR: No valid questions and answers could be generated.")
        exit(1)
    
    print(f"Successfully generated {len(quiz)} quiz questions.")
    
    # Output the formatted JavaScript
    js_quiz = format_javascript_quiz(quiz)
    print("\nQuiz data in JavaScript format:")
    print(js_quiz)
