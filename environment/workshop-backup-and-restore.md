# Saving Your Workshop Work and Restoring It Later

These steps let you copy your workshop folder off your AWS EC2 workshop instance to your own computer. They also cover putting it back onto a new workshop instance later.

Each section has instructions for **macOS**, **Linux** and **Windows**.

---

## Before you start

### What you need

| Item | Where to find it |
| --- | --- |
| Your instance's **IP address** | Available in Splunk Show |
| The **username** | Always `splunk` |
| The **SSH port** | Always `2222` (not the usual 22) |
| Your instance **password** | Available in Splunk Show |

You logged in during the workshop with a command like this:

```bash
ssh -p 2222 splunk@3.252.74.164
```

In the commands below, replace `YOUR_INSTANCE_IP` with your own IP address and replace `WORKSHOP_FOLDER` with the folder you created.

---

## Part 1 – Copy your work from the instance to your computer

Do this **before the workshop instance is shut down**. Once the instance is terminated, your work cannot be recovered.

### Step 1 – Log in to the instance  **[on your computer]**

```bash
ssh -p 2222 splunk@YOUR_INSTANCE_IP
```

Enter your password when prompted.

### Step 2 – Pack your folder into a single file  **[on the instance]**

```bash
cd ~
tar -czf workshop-backup.tar.gz WORKSHOP_FOLDER
```

This creates one compressed file, `workshop-backup.tar.gz`, in your home directory that contains your whole folder. One file is quicker and safer to copy than many small ones. It also keeps file permissions (for example, executable scripts) intact.

Check that it worked:

```bash
ls -lh ~/workshop-backup.tar.gz
tar -tzf ~/workshop-backup.tar.gz | head -20
```

The first command shows the file and its size. The second lists the first 20 files inside it. Each should start with `WORKSHOP_FOLDER/`.

### Step 3 – Log out of the instance  **[on the instance]**

```bash
exit
```

You are now back on your own computer.

### Step 4 – Download the file **[on your computer]**

**macOS / Linux:**

```bash
scp -P 2222 splunk@YOUR_INSTANCE_IP:workshop-backup.tar.gz ~/Downloads/
```

**Windows (PowerShell):**

```powershell
scp -P 2222 splunk@YOUR_INSTANCE_IP:workshop-backup.tar.gz "$HOME\Downloads\"
```

Enter your instance password when prompted. When the progress line reaches `100%`, the download has finished.

The file is now in your **Downloads** folder.

---

## Part 2 – Restore your work onto a new workshop instance

This assumes the new instance is the **same workshop image**: user `splunk`, port `2222`, a password supplied by SPlunk Show. Only the **IP address** will be different.

In the commands below, replace `NEW_INSTANCE_IP` with the new IP address.

### Step 1 – Upload the backup **[on your computer]**

**macOS / Linux:**

```bash
scp -P 2222 ~/Downloads/workshop-backup.tar.gz splunk@NEW_INSTANCE_IP:
```

**Windows (PowerShell):**

```powershell
scp -P 2222 "$HOME\Downloads\workshop-backup.tar.gz" splunk@NEW_INSTANCE_IP:
```

The **colon (`:`) at the end is required**. It means "the home directory on the instance". Without it, `scp` makes a local copy of the file named `splunk@NEW_INSTANCE_IP` instead of uploading it.

Answer `yes` to the first-connection question, then enter the **new** instance's password.

### Step 2 – Log in to the new instance **[on your computer]**

```bash
ssh -p 2222 splunk@NEW_INSTANCE_IP
```

### Step 3 – Unpack your backup **[on the instance]**

```bash
cd ~
tar -xzf workshop-backup.tar.gz
```

### Step 4 – Check the restore **[on the instance]**

```bash
ls -la ~/WORKSHOP_FOLDER
```

You should see your files, with the same dates and permissions they had before.

---

## Quick reference

| Command | Where |
| ------- | ----- |
| **BACKUP** | |
| ssh -p 2222 splunk@YOUR_INSTANCE_IP | Your Computer |
| cd ~ && tar -czf workshop-backup.tar.gz WORKSHOP_FOLDER | Instance |
| exit | Instance |
| scp -P 2222 splunk@YOUR_INSTANCE_IP:workshop-backup.tar.gz ~/Downloads/ | Mac/Linux |
| scp -P 2222 splunk@YOUR_INSTANCE_IP:workshop-backup.tar.gz "$HOME\Downloads\" | Windows PowerShell |
| **RESTORE** | |
| scp -P 2222 ~/Downloads/workshop-backup.tar.gz splunk@NEW_INSTANCE_IP: | Mac/Linux |
| scp -P 2222 "$HOME\Downloads\workshop-backup.tar.gz" splunk@NEW_INSTANCE_IP: | Windows PowerShell |
| ssh -p 2222 splunk@NEW_INSTANCE_IP | Your Computer |
| cd ~ && tar -xzf workshop-backup.tar.gz | Instance |

