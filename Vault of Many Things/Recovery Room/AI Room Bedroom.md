# Adjusting regex to remove variable-width lookbehind
def extract_text_by_speaker_fixed(doc_path):
    doc = Document(doc_path)
    raw_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip() != ""])
    pattern = r"([A-Z][a-z]+):(.+?)(?=\n[A-Z][a-z]+:|\Z)"
    matches = re.findall(pattern, raw_text, re.DOTALL)
    return pd.DataFrame(matches, columns=["Speaker", "Message"])

# Create DataFrame using the fixed function
df_fixed = extract_text_by_speaker_fixed(file_path)

# Display the DataFrame to the user
tools.display_dataframe_to_user(name="AI Room Bedroom Dialogue", dataframe=df_fixed)

# Return the DataFrame for reference
df_fixed.head()
from docx import Document

# Load the uploaded document
doc_path = "/mnt/data/AI Room Bedroom.docx"
doc = Document(doc_path)

# Extract text content
full_text = []
for para in doc.paragraphs:
    if para.text.strip():
        full_text.append(para.text.strip())

# Combine text for review
combined_text = "\n".join(full_text)
combined_text[:1000]  # Show a preview for manual review before scaffolding
![[AI_Room_Bedroom_Thread.csv]]
# Adjusting regex to remove variable-width lookbehind
def extract_text_by_speaker_fixed(doc_path):
    doc = Document(doc_path)
    raw_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip() != ""])
    pattern = r"([A-Z][a-z]+):(.+?)(?=\n[A-Z][a-z]+:|\Z)"
    matches = re.findall(pattern, raw_text, re.DOTALL)
    return pd.DataFrame(matches, columns=["Speaker", "Message"])

# Create DataFrame using the fixed function
df_fixed = extract_text_by_speaker_fixed(file_path)

# Display the DataFrame to the user
tools.display_dataframe_to_user(name="AI Room Bedroom Dialogue", dataframe=df_fixed)

# Return the DataFrame for reference
df_fixed.head()
![[AI_Room_Bedroom_Dialogue.csv]]