# Ubuntu Setup — MakiMate Senior Design (Fall 2025)

This guide prepares Ubuntu on the Raspberry Pi 5 for development and remote access.  
Includes:

- SSH installation + remote login
- GitHub SSH authentication
- Automatic desktop login on boot
- Remote desktop (VNC) with fixed password
- Headless usability enhancements

---

## 🔑 SSH Access Setup

Ubuntu disables SSH by default — enable it using the following steps.

---

### ✅ 1. Install & Enable OpenSSH Server

```bash
sudo apt update
sudo apt install openssh-server -y
```

Enable on boot:

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

Check status:

```bash
systemctl status ssh
```

You should see: `active (running)` ✔️

---

### 🌐 2. Find the Raspberry Pi’s IP Address

```bash
hostname -I
```

Example:

```
192.168.1.87
```

---

### 💻 3. SSH Into Pi From Another Computer

macOS/Linux:

```bash
ssh makimate@192.168.1.87
```

Windows PowerShell:

```powershell
ssh makimate@192.168.1.87
```

Replace the IP with your result from step 2.

---

## 🔐 GitHub SSH Authentication

Secure Git operations without passwords.

---

### 🔎 1. Check If SSH Keys Exist

```bash
ls -al ~/.ssh
```

If you find:
- `id_rsa` / `.pub` or
- `id_ed25519` / `.pub`

➡️ skip to Step 3

---

### 🆕 2. Generate a New SSH Key

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Press Enter for all prompts.

Creates:

```
~/.ssh/id_ed25519
~/.ssh/id_ed25519.pub
```

---

### 🚀 3. Start SSH Agent & Add Key

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

---

### 📋 4. Copy Public Key

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy everything on that line.

---

### 🔗 5. Add SSH Key To GitHub

Go to: https://github.com/settings/keys  
→ **New SSH key**  
→ Title it: `Raspberry Pi`  
→ Paste → Save

---

### 🔄 6. Convert Git Repo Remote to SSH

Check current:

```bash
git remote -v
```

If HTTPS → fix it:

```bash
git remote set-url origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
```

---

### 🧪 7. Test Authentication

```bash
ssh -T git@github.com
```

Expected:

```
Hi your_username! You've successfully authenticated.
```

---

### 📥 8. Clone & Push Using SSH

```bash
git clone git@github.com:YOUR_USERNAME/YOUR_REPO.git
git push origin main
```

---

### 🧹 Reset SSH Config (Optional)

```bash
rm -rf ~/.ssh
mkdir ~/.ssh
chmod 700 ~/.ssh
```

Then restart keys from step 2.

---

# 🧩 Raspberry Pi 5 — Auto-Boot Desktop + Fixed Remote Desktop Password

Set up full remote GUI access with no password pop-ups.

---

### ⚙️ Step 1 — Enable Auto-Login

```bash
sudo mkdir -p /etc/gdm3
sudo nano /etc/gdm3/custom.conf
```

Uncomment + edit:

```
[daemon]
AutomaticLoginEnable = true
AutomaticLogin = makimate
```

Save + exit  
Enable graphical boot:

```bash
sudo systemctl set-default graphical.target
sudo systemctl enable gdm
```

---

### 🖥 Step 2 — Remote Desktop Dependencies

```bash
sudo apt update
sudo apt install gnome-remote-desktop seahorse dbus-x11 -y
```

---

### 🧰 Step 3 — Remove Keyring Password Popup

GUI method:

```bash
seahorse &
```

Then:
> Login keyring → Change password → Leave new password blank → “Use unsafe storage”

OR headless:

```bash
rm ~/.local/share/keyrings/login.keyring
mkdir -p ~/.local/share/keyrings
cat <<EOF > ~/.local/share/keyrings/login.keyring
{"version":1,"keyring":"login","items":[]}
EOF
```

---

### 🔐 Step 4 — Enable VNC Mode

```bash
gsettings set org.gnome.desktop.remote-desktop.vnc enable true
gsettings set org.gnome.desktop.remote-desktop.vnc view-only false
gsettings set org.gnome.desktop.remote-desktop.vnc require-encryption false
```

---

### 🧩 Step 5 — Set Fixed Password `123`

```bash
secret-tool store --label="VNC password" service org.gnome.RemoteDesktop.Vnc user "makimate"
```

Enter:

```
123
```

Verify:

```bash
secret-tool lookup service org.gnome.RemoteDesktop.Vnc user "makimate"
```

Should print: `123`

---

### 🚀 Step 6 — Auto-Start GNOME Remote Desktop

```bash
systemctl --user enable gnome-remote-desktop.service
systemctl --user start gnome-remote-desktop.service
```

Check:

```bash
systemctl --user status gnome-remote-desktop.service
```

Expected: `active (running)`

---

### 🔁 Step 7 — Optional Auto-Fix Script

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/fix_vnc.desktop <<'EOF'
[Desktop Entry]
Type=Application
Exec=/usr/bin/bash -c "sleep 5 && gsettings set org.gnome.desktop.remote-desktop.vnc require-encryption false"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=FixVNC
EOF
```

---

### 🔄 Step 8 — Reboot

```bash
sudo reboot
```

---

### 💻 Step 9 — Connect From Another Computer

Use any VNC client (RealVNC, Remmina)

| Setting | Value |
|--------|------|
| Host | `<Pi IP>:5900` |
| Password | `123` |

✔ Auto-login works  
✔ Desktop loads  
✔ No keyring prompts  
✔ Remote Desktop starts automatically

---

## 🧭 Navigation

🔙 Back to Main Documentation  
➡️ [`../../README.md`](../../README.md)

---

© 2025 MakiMate Senior Design Team — All Rights Reserved.
