# Automated App Interaction System

## Project Overview
This project implements an automated system for interacting with a mobile application using Appium and Android Emulator. It's designed to automate the process of booking classes through a specific fitness studio application (Glofox).

## Key Components

### Core Technologies
- **Appium**: Mobile app automation framework
- **Android Emulator**: Virtual device environment
- **Python**: Primary programming language
- **Batch Script**: Windows automation script

### Main Features

1. **Automated Initialization**
   - Automatic startup of Android Emulator
   - Appium server management
   - WiFi connection verification
   - Process cleanup and management

2. **Robust Error Handling**
   - Maximum retry attempts: 3
   - Comprehensive logging system
   - Screenshot capture for verification
   - Automatic process recovery

3. **Automated App Navigation**
   - Studio search functionality
   - Automated login process
   - Class booking system
   - Dynamic slot selection

## Technical Architecture

### 1. Batch Script (`demo.bat`)
- Manages process cleanup (QEMU, Emulator, ADB, Node)
- Handles retry logic (max 3 attempts)
- Coordinates Appium server startup
- Controls Python script execution

### 2. Python Implementation (`demo.py`)
- **Main Classes**:
  - `GlofoxBooker`: Core booking functionality
  - Various utility functions for device management

- **Key Features**:
  - Comprehensive logging system
  - Screenshot capture
  - Dynamic coordinate-based interaction
  - Permission handling
  - Session management

### System Flow

1. **Initialization Phase**
   ```
   - Kill existing processes
   - Start Appium server
   - Launch Android Emulator
   ```

2. **Application Phase**
   ```
   - Launch target application
   - Handle permissions
   - Execute search
   - Perform login
   - Navigate to booking
   - Complete booking process
   ```

3. **Cleanup Phase**
   ```
   - Stop Emulator
   - Stop Appium
   - Log completion
   ```

## Configuration

### Key Parameters
```python
APPIUM_SERVER = 'http://127.0.0.1:4723'
APP_PACKAGE = '[YOUR APP PACKAGE]'
APP_ACTIVITY = '[YOUR APP ACTIVITY]'
DEVICE_NAME = '[YOUR DEVICE NAME]'
WAIT_TIME = 10
```

### Slot Mapping
```python
SLOT_COORDINATES = {
    1: (500, 650),   # 1st slot
    2: (516, 1003),  # 2nd slot
    3: (461, 1372),  # 3rd slot
    4: (388, 1718),  # 4th slot
    5: (377, 2017),  # 5th slot
    6: (386, 2154)   # 6th slot
}
```

## Error Handling & Logging

### Logging System
- File-based logging with timestamp
- Console output for real-time monitoring
- Screenshot capture at critical points
- Detailed error tracking

### Recovery Mechanisms
- Automatic retry on failure
- Process cleanup before retries
- WiFi connection verification
- Appium server health checks

## Best Practices Implemented

1. **Resource Management**
   - Proper cleanup of processes
   - Systematic shutdown procedures
   - Memory management

2. **Error Recovery**
   - Graceful error handling
   - Automatic retry mechanisms
   - Comprehensive logging

3. **Performance Optimization**
   - Efficient process management
   - Optimized wait times
   - Resource cleanup

4. **Security**
   - Credential management
   - Permission handling
   - Session management

## Future Improvements

1. **Potential Enhancements**
   - Dynamic coordinate calculation
   - Enhanced error recovery
   - Configuration file implementation
   - Multi-device support

2. **Scalability Options**
   - Parallel execution support
   - Cloud emulator integration
   - Enhanced monitoring capabilities

## Setup Requirements

### Prerequisites
- Python 3.x
- Android SDK
- Appium Server
- Required Python packages:
  - appium-python-client
  - selenium
  - logging

### Environment Setup
1. Install Android SDK and configure emulator
2. Install Appium and dependencies
3. Configure Python environment
4. Set up logging directory

## Usage Instructions

1. Configure application credentials
2. Set up target app package and activity
3. Configure slot preferences
4. Run batch script:
   ```bash
   demo.bat
   ```

## Maintenance

### Regular Tasks
- Log file management
- Screenshot cleanup
- Configuration updates
- Dependency updates

### Troubleshooting
- Check Appium server status
- Verify emulator configuration
- Review log files
- Validate network connectivity