import time
from datetime import datetime
from openpyxl import Workbook

def main():
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "LogData"
    
    
    worksheet.append(["Timestamp", "Value"])
    
    counter = 0
    log_duration = 10  
    start_time = time.time()

    print("Logging data for {} seconds...".format(log_duration))
    
    while True:
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        counter += 1

        worksheet.append([now, counter])
        print(f"Logged: {now}, Value: {counter}")

        if time.time() - start_time >= log_duration:
            break
        time.sleep(1)
    
    
    filename = "log_data.xlsx"
    workbook.save(filename)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    main()
