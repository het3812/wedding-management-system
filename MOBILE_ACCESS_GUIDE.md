# 📱 Mobile Access Guide - Run on Same WiFi

## ✅ Changes Made

Modified `app.py` to allow access from other devices on the same network:
- Changed `host='127.0.0.1'` to `host='0.0.0.0'`
- This allows external connections from devices on your WiFi

## 🚀 How to Access from Mobile

### Step 1: Find Your Computer's IP Address

**On Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" under your WiFi adapter (e.g., `192.168.1.100`)

**On Mac/Linux:**
```bash
ifconfig
```
or
```bash
ip addr show
```
Look for your WiFi IP address (e.g., `192.168.1.100`)

### Step 2: Start the Flask App

```bash
python app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
* Running on http://192.168.1.100:5000  (your actual IP)
```

### Step 3: Access from Mobile

1. **Ensure both devices are on the same WiFi network**
2. **Open browser on your mobile**
3. **Enter the URL**: `http://YOUR_COMPUTER_IP:5000`

**Example:**
```
http://192.168.1.100:5000
```

## 📋 Quick Steps

1. ✅ Modified app.py (already done)
2. Find your computer's IP address
3. Start Flask: `python app.py`
4. On mobile, open: `http://YOUR_IP:5000`

## 🔥 Firewall Settings (If Connection Fails)

### Windows Firewall

If you can't connect, allow Python through Windows Firewall:

1. Open **Windows Defender Firewall**
2. Click **Allow an app through firewall**
3. Click **Change settings**
4. Find **Python** or click **Allow another app**
5. Browse to your Python executable
6. Check both **Private** and **Public** networks
7. Click **OK**

**Or run this command as Administrator:**
```bash
netsh advfirewall firewall add rule name="Flask App" dir=in action=allow protocol=TCP localport=5000
```

### Quick Firewall Rule (PowerShell as Admin)

```powershell
New-NetFirewallRule -DisplayName "Flask App" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## 🧪 Testing

### Test on Computer First
```
http://localhost:5000
http://127.0.0.1:5000
```

### Test with Computer's IP
```
http://YOUR_IP:5000
```

### Test from Mobile
```
http://YOUR_IP:5000
```

## 📱 Mobile Browser Tips

- Use **Chrome** or **Safari** for best compatibility
- Bookmark the URL for easy access
- The site is responsive and mobile-friendly
- All features work on mobile

## 🔒 Security Notes

- This setup is for **local development only**
- Only devices on your WiFi can access
- Don't use this configuration for production
- For production, use a proper web server (nginx, Apache)

## 🐛 Troubleshooting

### Can't Connect from Mobile

1. **Check WiFi**: Both devices on same network?
2. **Check IP**: Is the IP address correct?
3. **Check Firewall**: Is port 5000 allowed?
4. **Check Flask**: Is the app running?
5. **Try ping**: Can mobile ping your computer?

### Find IP Address Issues

**Windows - Quick Method:**
```bash
ipconfig | findstr IPv4
```

**Get all network info:**
```bash
ipconfig /all
```

### Port Already in Use

If port 5000 is busy, change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

Then access: `http://YOUR_IP:8080`

### Connection Refused

1. Stop Flask app
2. Add firewall rule (see above)
3. Restart Flask app
4. Try again from mobile

## 📊 Example Setup

```
Computer (Windows):
- IP: 192.168.1.100
- Running: python app.py
- Flask on: http://0.0.0.0:5000

Mobile (Android/iPhone):
- Connected to: Same WiFi
- Browser: Chrome
- Access: http://192.168.1.100:5000
```

## ✅ Verification Checklist

- [ ] Modified app.py (host='0.0.0.0')
- [ ] Found computer's IP address
- [ ] Started Flask app
- [ ] Both devices on same WiFi
- [ ] Firewall allows port 5000
- [ ] Tested on computer first
- [ ] Accessed from mobile browser

## 🎯 Quick Command Reference

```bash
# Find IP (Windows)
ipconfig

# Find IP (Mac/Linux)
ifconfig

# Start Flask
python app.py

# Add firewall rule (Windows Admin)
netsh advfirewall firewall add rule name="Flask" dir=in action=allow protocol=TCP localport=5000

# Test connection (from mobile or computer)
ping YOUR_COMPUTER_IP
```

## 📱 Mobile URL Format

```
http://[YOUR_COMPUTER_IP]:5000

Examples:
http://192.168.1.100:5000
http://192.168.0.50:5000
http://10.0.0.5:5000
```

## 🎉 Success!

Once connected, you can:
- ✅ Login as Admin, Host, or Vendor
- ✅ Manage bookings
- ✅ View receipts
- ✅ Track commissions
- ✅ All features work on mobile!

---

**Note**: Remember to change back to `host='127.0.0.1'` if you only want local access later.
