# 📋 REMOTE SETTINGS DIRECTORY

## ⚙️ Files You Can Edit to Control All Trackers

All files in this `settings/` directory can be edited and pushed to GitHub to automatically update all deployed pregnancy trackers. Changes will be applied on the next auto-update cycle.

### 🎯 Configurable Settings Files:

#### 1. **display_config.json** - Display Update Timing
Controls how often the e-ink display refreshes and switches screens.
- `frequency_minutes`: How often to update display (default: 10)
- `switch_interval_minutes`: How often to alternate screens (default: 20)
- `update_schedule`: Use "interval" or "custom" times

#### 2. **pregnancy.json.example** - Due Date Configuration
Template for the pregnancy due date configuration.
- Copy to `config.json` on each Pi with correct date
- `expected_birth_date`: Format "YYYY-MM-DD"

### ⚠️ DO NOT EDIT Scripts in Root Directory
The `.sh` scripts in the root directory are system scripts and should NOT be edited for configuration changes:
- ❌ auto_update.sh
- ❌ manage_display_cron.sh
- ❌ setup_auto_update.sh
- ❌ monitor_updates.sh

### 📝 How to Make Changes:

1. **Edit settings files** in this directory
2. **Commit and push** to GitHub
3. **Wait** for next auto-update cycle (or trigger manually)
4. Changes apply automatically to all Pis!

### 🔄 Update Cycle:
- Default: Every 12 hours
- Manual trigger: SSH to Pi and run `~/e-ink-pregnancy-tracker/auto_update.sh`

---
*Only modify files in this settings/ directory for remote configuration changes*