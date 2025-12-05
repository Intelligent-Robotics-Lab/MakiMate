# Ubuntu Setup — MakiMate Senior Design (Fall 2025)

📌 This guide covers essential Ubuntu setup for development and secure access to the MakiMate robot system, including:
- Enabling SSH access
- Locating the Raspberry Pi on your network
- Configuring GitHub SSH authentication for secure code management

---

## 🔑 SSH Access Setup

Ubuntu does *not* enable SSH by default — follow the steps below to allow remote login.

---

### ✅ 1. Install & Enable OpenSSH Server

```bash
sudo apt update
sudo apt install openssh-server -y
```

Enable SSH at boot and start service:

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

Verify SSH status:

```bash
systemctl status ssh
```

You should see: `active (running)` ✔️

---

### 🌐 2. Find the Raspberry Pi’s IP Address

Run:

```bash
hostname -I
```

Example output:

```
192.168.1.87
```

Use that address for remote SSH access.

---

### 💻 3. Connect To The Raspberry Pi

From macOS/Linux:

```bash
ssh makimate@192.168.1.87
```

From Windows PowerShell:

```powershell
ssh makimate@192.168.1.87
```

Replace the IP with the value from step 2.

---

## 🔐 GitHub SSH Key Configuration

This allows **password-less pushing & pulling** from GitHub — highly recommended.

---

### 🔎 1. Check If SSH Keys Already Exist

```bash
ls -al ~/.ssh
```

If you see files like:

- `id_rsa` & `id_rsa.pub`  
- `id_ed25519` & `id_ed25519.pub`  

➡️ You can skip to Step 3  
If not → continue.

---

### 🆕 2. Generate a New SSH Key

Recommended modern format:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

When prompted:
- Press **Enter** for location
- Press **Enter twice** for no passphrase

This creates:

```
~/.ssh/id_ed25519
~/.ssh/id_ed25519.pub
```

---

### 🚀 3. Start SSH Agent & Add Your Key

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

---

### 📋 4. Copy Your Public Key

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the full string starting with `ssh-ed25519 AAAA…`

---

### 🔗 5. Add Your Key to GitHub

1️⃣ Visit: **https://github.com/settings/keys**  
2️⃣ Click: **New SSH Key**  
3️⃣ Title: `Raspberry Pi`  
4️⃣ Paste → Save

---

### 🔄 6. Switch GitHub Remotes to SSH

Check current remote:

```bash
git remote -v
```

If it shows `https://github.com/...` → fix it:

```bash
git remote set-url origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
```

---

### 🧪 7. Test GitHub SSH Connection

```bash
ssh -T git@github.com
```

Expected success message:

```
Hi your_username! You've successfully authenticated.
```

---

### 📥 8. Clone & Push Over SSH

Clone:

```bash
git clone git@github.com:YOUR_USERNAME/YOUR_REPO.git
```

Push examples:

```bash
git push origin main
```

---

## 🧹 Reset SSH If Something Went Wrong (Optional)

```bash
rm -rf ~/.ssh
mkdir ~/.ssh
chmod 700 ~/.ssh
```

Then restart from Step 2.

---

## 🧭 Navigation

🔙 Return to Main Documentation  
➡️ [`../../README.md`](../../README.md)

---

© 2025 MakiMate Senior Design Team — All Rights Reserved.
