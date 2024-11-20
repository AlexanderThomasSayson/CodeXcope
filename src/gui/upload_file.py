from tkinter import filedialog, messagebox
from src.data_processing.process_fund_transfer_logs import process_fund_transfer_logs
from src.data_processing.process_rds_logs import process_rds_logs
from src.data_processing.process_promotexter_logs import process_promotexter_data

# Function for the upload buttons
def upload_file(button):
    file_path = filedialog.askopenfilename()
    if file_path:
        if button == "Fund Transfer Logs":
            process_fund_transfer_logs(file_path)
        elif button == "RDS Logs":
            process_rds_logs(file_path)
        elif button == "Promotexter Logs":
            process_promotexter_data(file_path)
        messagebox.showinfo("Success!", f"{button} execution successful")