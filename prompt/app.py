# Define a function to create the formatted text using the actual column names
def create_formatted_text(row):
    # Construct the sentence using the values from the row, handling missing data
    parts = [
        f"{row['질병명']}은(는)" if not pd.isnull(row['질병명']) else "<질병명>은(는)",
        f"{row['진료과']}에서 주로 진료하며," if not pd.isnull(row['진료과']) else "<진료과>에서 주로 진료하며,",
        f"증상은 {row['증상']}이(가) 있다." if not pd.isnull(row['증상']) else "증상은 <증상>이(가) 있다.",
        f"관련된 질환으로는 {row['관련질환']}이(가) 있으며," if not pd.isnull(row['관련질환']) else "관련된 질환으로는 <관련질환>이(가) 있으며,",
        f"같은 이름으로는 {row['동의어']}과(와) 같은 명칭이 존재하고," if not pd.isnull(row['동의어']) else "같은 이름으로는 <동의어>과(와) 같은 명칭이 존재하고,",
        f"{row['부위']}과(와) 관련 있는 질환이다." if not pd.isnull(row['부위']) else "<부위>과(와) 관련 있는 질환이다."
    ]
    return ' '.join(part for part in parts)

# Apply the function to each row in the DataFrame to create the formatted text
df_check['H'] = df_check.apply(create_formatted_text, axis=1) # 여기에 데이터 가공할 파일경로

# Save the updated DataFrame back to an Excel file
final_corrected_output_path = '/mnt/data/sibumcase2_final_corrected.xlsx' # 여기에 만들 파일이름
df_check.to_excel(final_corrected_output_path, index=False)

final_corrected_output_path