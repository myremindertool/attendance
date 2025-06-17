
import streamlit as st
import pandas as pd
from io import BytesIO

def check_unapproved_absences(attendance_df, leave_df):
    # Normalize and prepare columns
    attendance_df['Date'] = pd.to_datetime(attendance_df['Date'], errors='coerce')
    leave_df['Leave Start Date'] = pd.to_datetime(leave_df['Leave Start Date'], errors='coerce')
    leave_df['Leave End Date'] = pd.to_datetime(leave_df['Leave End Date'], errors='coerce')

    attendance_df['Name_norm'] = attendance_df['Name'].str.strip().str.lower()
    leave_df['Name of Employee'] = leave_df['Name of Employee'].str.strip().str.lower()

    # Filter absentees
    absent_df = attendance_df[attendance_df['Exception'].str.contains('Absence', na=False)].copy()
    absent_df['Leave_Status'] = 'Unapproved Absence'

    for idx, row in absent_df.iterrows():
        person = row['Name_norm']
        date = row['Date']
        person_leaves = leave_df[leave_df['Name of Employee'] == person]

        for _, leave_row in person_leaves.iterrows():
            if pd.notnull(leave_row['Leave Start Date']) and pd.notnull(leave_row['Leave End Date']):
                if leave_row['Leave Start Date'] <= date <= leave_row['Leave End Date']:
                    absent_df.at[idx, 'Leave_Status'] = 'Leave Applied'
                    break

    # Merge result back
    attendance_df = attendance_df.merge(
        absent_df[['Date', 'Name_norm', 'Leave_Status']],
        on=['Date', 'Name_norm'],
        how='left'
    )
    attendance_df.drop(columns=['Name_norm'], inplace=True)

    # Format date to DD/MM/YYYY
    attendance_df['Date'] = attendance_df['Date'].dt.strftime('%d/%m/%Y')

    return attendance_df

# Streamlit app
def main():
    st.title("📝 Absence Checker Tool")
    st.markdown("Upload the **Attendance Sheet** and the **Leave Application Sheet** below:")

    att_file = st.file_uploader("Upload Daily Attendance Sheet", type=["xlsx"])
    leave_file = st.file_uploader("Upload Leave Application Sheet", type=["xlsx"])

    if att_file and leave_file:
        att_df = pd.read_excel(att_file)
        leave_df = pd.read_excel(leave_file)

        result_df = check_unapproved_absences(att_df, leave_df)

        st.success("✅ Comparison complete! Download the processed file below:")

        output = BytesIO()
        result_df.to_excel(output, index=False)
        st.download_button("📥 Download Reviewed Attendance Sheet",
                           data=output.getvalue(),
                           file_name="Reviewed_Attendance.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()
