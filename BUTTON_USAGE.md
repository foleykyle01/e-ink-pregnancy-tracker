# Button Usage Guide

The pregnancy tracker now uses the 4 physical buttons on the e-ink display to switch between different screens.

## Button Mappings

- **Button 1**: Progress Screen - Shows pregnancy progress percentage and timeline
- **Button 2**: Size Comparison Screen - Shows baby size compared to fruits/objects
- **Button 3**: Appointments Screen - Shows next upcoming appointment details
- **Button 4**: Baby Info Screen - Shows current week, days until due, and trimester

## Managing Appointments

To update appointment information, edit the `appointments.json` file. The file format is:

```json
{
    "appointments": [
        {
            "date": "YYYY-MM-DD",
            "time": "HH:MM AM/PM",
            "type": "Appointment Type",
            "location": "Location",
            "notes": "Any notes"
        }
    ]
}
```

The system will automatically show the next upcoming appointment on the appointments page.

## GPIO Pin Configuration

The buttons use the following GPIO pins (BCM numbering):
- Button 1 (KEY1): GPIO 5
- Button 2 (KEY2): GPIO 6
- Button 3 (KEY3): GPIO 13
- Button 4 (KEY4): GPIO 19

## Power Saving

The display goes to sleep after each button press to save power. Pressing any button will wake it up and display the corresponding screen.