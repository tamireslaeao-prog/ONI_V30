# ONI API Documentation

> **Base URL:** `http://localhost:8000`  
> **Version:** 24.3

---

## Health & Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check - returns system status |
| `/api/ready` | GET | Readiness check - returns if system is ready |
| `/api/info` | GET | System information (version, mode) |

---

## Vision

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/vision/capture` | GET | Capture screenshot |
| `/api/vision/analyze` | POST | Analyze image with AI |
| `/api/hybrid-vision/desktop` | GET | Desktop analysis with annotations |
| `/api/hybrid-vision/web` | GET | Web page analysis |

---

## Actions (Mouse/Keyboard)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/click` | GET | Click at x,y coordinates |
| `/api/type` | GET | Type text |
| `/api/keys` | GET | Send keyboard shortcuts |
| `/api/focus` | GET | Focus window by title |
| `/api/open` | GET | Open application |

---

## ONI Core

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/oni/actions` | POST | Execute ONI action |
| `/api/oni/artmaster/draw/*` | POST | Drawing primitives |
| `/api/oni/autonomous/startup` | GET | Autonomous mode startup |
| `/api/oni/canvas` | GET | Get canvas limits |
| `/api/oni/window` | GET | Window management |

---

## Photoshop Bridge

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/photoshop/execute` | POST | Execute JSX script |
| `/api/photoshop/action` | POST | Run PS action |

---

## Blender Bridge

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/blender/execute` | POST | Execute Python script |

---

## Example Usage

### Capture Screenshot
```bash
curl http://localhost:8000/api/vision/capture
```

### Click at Position
```bash
curl "http://localhost:8000/api/click?x=500&y=300"
```

### Type Text
```bash
curl "http://localhost:8000/api/type?text=Hello%20World"
```

### Send Keyboard Shortcut
```bash
curl "http://localhost:8000/api/keys?keys=ctrl,s"
```

### Focus Window
```bash
curl "http://localhost:8000/api/focus?title=Photoshop"
```
