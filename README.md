# E4ClientAPI
Empatica E4 Client API to log HR, EDA, IBI and BVP from Empatica Windows Streaming Server. 

Reference: http://developer.empatica.com/windows-streaming-server-usage.html

# Run 
1. Run the python code using "python e4_api.py" from command line. 
2. Make sure to update the timer, device_id and ip_address from the e4_api.py
3. Press CRTL + C to forcefully close the app
4. File will be saved in the same directory. 

# Known Issue: 
1. After the expiration of the timer, app may not close and save automatically. 
 Temp Fix: Press CRTL + C to forcefully close and save once the timer expires. 
