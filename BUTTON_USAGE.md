# Button Usage Guide

The pregnancy tracker uses the 4 physical buttons on the e-ink display to switch between different screens.

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
            "type": "Appointment Type"
        }
    ]
}
```

Note: The "location" and "notes" fields are optional and not displayed (for family viewing privacy).

The system will automatically show the next upcoming appointment on the appointments page.

## GPIO Pin Configuration

The buttons use the following GPIO pins (BCM numbering):
- Button 1 (KEY1): GPIO 5
- Button 2 (KEY2): GPIO 6
- Button 3 (KEY3): GPIO 13
- Button 4 (KEY4): GPIO 19

## Technical Notes

- The display initializes first, then buttons to avoid GPIO conflicts
- Button presses have a 1-second debounce to prevent accidental multiple triggers
- The display remains active (not sleeping) to ensure responsive button presses