import asyncio
import pandas as pd
from datetime import datetime
import time
import atexit


# Connect and Subscribe to data stream
async def connect_and_subscribe_to_data(message):
    reader, writer = await asyncio.open_connection('192.168.1.8', 28000)
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    await subscribe_data(reader, writer, "device_subscribe gsr ON\n")
    await subscribe_data(reader, writer, "device_subscribe ibi ON\n")
    await subscribe_data(reader, writer, "device_subscribe bvp ON\n")

    await read_data_stream(reader, writer)

    print("Physiological Data Collection Done!")


# Subscribe to data stream
async def subscribe_data(reader, writer, message):
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(4096)
    print(f'Received: {data.decode()!r}')


# Read data stream from server
async def read_data_stream(reader, writer):
    start = time.time()
    while True:
        data = await reader.read(4096)
        lines = data.decode().splitlines()
        # print(lines)
        handle_response_data(lines)
        end = time.time()
        elapsed_time = end - start
        if elapsed_time > default_end_time:  # Default timer  expired
            await save_and_close(writer)
            break


# Save and close connection
async def save_and_close(writer):
    d = datetime.today()
    time_date = d.strftime("%d_%B_%Y_%H_%M_%S")
    file_name = 'raw_data_' + time_date
    gsr_data.to_csv(file_name + "-gsr.csv")
    bvp_data.to_csv(file_name + "-bvp.csv")
    hr_data.to_csv(file_name + "-hr.csv")
    ibi_data.to_csv(file_name + "-ibi.csv")

    print('Close the connection')
    writer.close()
    await writer.wait_closed()


# Response Handler
def handle_response_data(lines):
    global gsr_data
    global bvp_data
    global ibi_data
    global hr_data

    for line in lines:

        if line is not None:
            data_chunk = line.split(' ')

            if len(data_chunk) >= 3:
                timestamp = datetime.fromtimestamp(float(data_chunk[1])).strftime('%m-%d-%Y %H:%M:%S.%f')

                if data_chunk[0].startswith("E4_Gsr"):
                    new_row = {"Time": timestamp, "GSR": data_chunk[2]}
                    gsr_data = gsr_data.append(new_row, ignore_index=True)
                    print(gsr_data.tail())

                elif data_chunk[0].startswith("E4_Bvp"):
                    new_row = {"Time": timestamp, "BVP": data_chunk[2]}
                    bvp_data = bvp_data.append(new_row, ignore_index=True)
                    print(bvp_data.tail())

                elif data_chunk[0].startswith("E4_Ibi"):
                    new_row = {"Time": timestamp, "IBI": data_chunk[2]}
                    ibi_data = ibi_data.append(new_row, ignore_index=True)
                    print(bvp_data.tail())

                elif data_chunk[0].startswith("E4_Hr"):
                    new_row = {"Time": timestamp, "HR": data_chunk[2]}
                    hr_data = hr_data.append(new_row, ignore_index=True)
                    print(bvp_data.tail())


# Method to save data if app is forcefully closed. (e.g., Participant can quit before the end of study time)
def forcefully_closed_handler():
    print("Application Closed Forcefully!")
    try:
        d = datetime.today()
        time_date = d.strftime("%d_%B_%Y_%H_%M_%S")
        file_name = 'raw_data_' + time_date
        gsr_data.to_csv(file_name + "-gsr.csv")
        bvp_data.to_csv(file_name + "-bvp.csv")
        hr_data.to_csv(file_name + "-hr.csv")
        ibi_data.to_csv(file_name + "-ibi.csv")

        # print('Close the connection')
        # writer.close()
        # writer.wait_closed()
    except RuntimeError as error:
        print("App Closed")


# Declare the Panda Data Frames
gsr_data = pd.DataFrame(columns=['Time', 'GSR'])
ibi_data = pd.DataFrame(columns=['Time', 'IBI'])
hr_data = pd.DataFrame(columns=['Time', 'HR'])
bvp_data = pd.DataFrame(columns=['Time', 'BVP'])
default_end_time = 3600  # Default timer in second.

# Main Function. Run using cmd and command pr ompt.
# Set the default timer
# Press CRTL + C to forcefully terminate data collection and save.

if __name__ == '__main__':
    atexit.register(forcefully_closed_handler)
    asyncio.run(connect_and_subscribe_to_data('device_connect 89CB11\n'))
