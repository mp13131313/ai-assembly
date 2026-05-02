import { useState, useEffect, useRef, useCallback } from "react";

// Example parameter sets from different "nights"
const PRESETS = {
  navigable: {
    label: "Open / Navigable",
    desc: "Distributed governance, multiple paths, no central control",
    params: {
      orientation: "toward",
      arousal: 0.7,
      valence: 0.85,
      pattern_mode: "passing_cloud",
      pattern_complexity: 0.7,
      palette: { darkness: 0.2, warmth: 0.8, brightness: 0.7, iridescence: 0.6 },
      dynamics: { wave_speed: 0.5, wave_count: 5, wave_direction: [0.3, -0.7], pulse_frequency: 0.4, turbulence: 0.3 },
      focal_points: [
        { x: 0.25, y: 0.35, intensity: 0.8 },
        { x: 0.7, y: 0.55, intensity: 0.6 },
        { x: 0.5, y: 0.8, intensity: 0.5 },
        { x: 0.85, y: 0.2, intensity: 0.4 },
      ],
      texture_intensity: 0.4,
    },
  },
  hostile: {
    label: "Constricted / Hostile",
    desc: "Centralised authority, single exit, rigid structure",
    params: {
      orientation: "away",
      arousal: 0.65,
      valence: 0.12,
      pattern_mode: "disruptive",
      pattern_complexity: 0.3,
      palette: { darkness: 0.82, warmth: 0.15, brightness: 0.18, iridescence: 0.08 },
      dynamics: { wave_speed: 0.7, wave_count: 1, wave_direction: [0.0, 0.8], pulse_frequency: 0.6, turbulence: 0.12 },
      focal_points: [{ x: 0.5, y: 0.5, intensity: 0.95 }],
      texture_intensity: 0.7,
    },
  },
  lateral: {
    label: "Lateral / Passing Through",
    desc: "Abstract philosophy with no spatial correlate",
    params: {
      orientation: "lateral",
      arousal: 0.2,
      valence: 0.5,
      pattern_mode: "uniform",
      pattern_complexity: 0.15,
      palette: { darkness: 0.4, warmth: 0.45, brightness: 0.3, iridescence: 0.2 },
      dynamics: { wave_speed: 0.2, wave_count: 1, wave_direction: [1.0, 0.0], pulse_frequency: 0.2, turbulence: 0.08 },
      focal_points: [],
      texture_intensity: 0.2,
    },
  },
  deimatic: {
    label: "Deimatic / Alarm",
    desc: "Octopus farming proposal — maximum threat",
    params: {
      orientation: "away",
      arousal: 0.95,
      valence: 0.05,
      pattern_mode: "deimatic",
      pattern_complexity: 0.9,
      palette: { darkness: 0.9, warmth: 0.6, brightness: 0.85, iridescence: 0.3 },
      dynamics: { wave_speed: 0.95, wave_count: 8, wave_direction: [0.0, 0.0], pulse_frequency: 0.9, turbulence: 0.8 },
      focal_points: [
        { x: 0.5, y: 0.5, intensity: 1.0 },
        { x: 0.2, y: 0.2, intensity: 0.7 },
        { x: 0.8, y: 0.8, intensity: 0.7 },
      ],
      texture_intensity: 0.9,
    },
  },
  river: {
    label: "River Co-governance",
    desc: "Multiple agents, adaptive flow, the river named as person",
    params: {
      orientation: "toward",
      arousal: 0.55,
      valence: 0.78,
      pattern_mode: "mottled",
      pattern_complexity: 0.6,
      palette: { darkness: 0.25, warmth: 0.55, brightness: 0.6, iridescence: 0.7 },
      dynamics: { wave_speed: 0.35, wave_count: 3, wave_direction: [0.2, -0.5], pulse_frequency: 0.3, turbulence: 0.25 },
      focal_points: [
        { x: 0.4, y: 0.5, intensity: 0.7 },
        { x: 0.6, y: 0.3, intensity: 0.5 },
      ],
      texture_intensity: 0.35,
    },
  },
};

// GLSL Vertex Shader
const vertexShaderSource = `
  attribute vec2 a_position;
  varying vec2 v_uv;
  void main() {
    v_uv = a_position * 0.5 + 0.5;
    gl_Position = vec4(a_position, 0.0, 1.0);
  }
`;

// GLSL Fragment Shader — the chromatophore engine
const fragmentShaderSource = `
  precision highp float;
  varying vec2 v_uv;
  
  uniform float u_time;
  uniform float u_arousal;
  uniform float u_valence;
  uniform float u_darkness;
  uniform float u_warmth;
  uniform float u_brightness;
  uniform float u_iridescence;
  uniform float u_wave_speed;
  uniform int u_wave_count;
  uniform vec2 u_wave_direction;
  uniform float u_pulse_frequency;
  uniform float u_turbulence;
  uniform float u_pattern_complexity;
  uniform float u_texture_intensity;
  uniform int u_pattern_mode; // 0=uniform, 1=mottled, 2=disruptive, 3=passing_cloud, 4=deimatic
  uniform int u_orientation; // 0=toward, 1=away, 2=lateral, 3=still
  
  // Focal points (up to 6)
  uniform int u_focal_count;
  uniform vec3 u_focals[6]; // xy = position, z = intensity
  
  // Hash functions for noise
  vec3 hash3(vec2 p) {
    vec3 q = vec3(
      dot(p, vec2(127.1, 311.7)),
      dot(p, vec2(269.5, 183.3)),
      dot(p, vec2(419.2, 371.9))
    );
    return fract(sin(q) * 43758.5453);
  }
  
  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
  }
  
  // Simplex-like noise
  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
  }
  
  // Fractal brownian motion
  float fbm(vec2 p, int octaves) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    for (int i = 0; i < 6; i++) {
      if (i >= octaves) break;
      value += amplitude * noise(p * frequency);
      frequency *= 2.0;
      amplitude *= 0.5;
    }
    return value;
  }
  
  // Voronoi for chromatophore cell structure
  float voronoi(vec2 p, float scale) {
    vec2 sp = p * scale;
    vec2 i = floor(sp);
    vec2 f = fract(sp);
    float minDist = 1.0;
    for (int x = -1; x <= 1; x++) {
      for (int y = -1; y <= 1; y++) {
        vec2 neighbor = vec2(float(x), float(y));
        vec3 h = hash3(i + neighbor);
        vec2 point = neighbor + h.xy - f;
        // Animate cell centers
        point += 0.3 * sin(u_time * u_pulse_frequency * 2.0 + h.z * 6.28) * vec2(h.x - 0.5, h.y - 0.5);
        float d = dot(point, point);
        minDist = min(minDist, d);
      }
    }
    return sqrt(minDist);
  }
  
  // Chromatophore expansion/contraction per cell
  float chromatophoreCell(vec2 p, float scale, float expansion) {
    float v = voronoi(p, scale);
    float cell = smoothstep(expansion * 0.6, expansion * 0.6 + 0.1, v);
    return 1.0 - cell;
  }
  
  // Passing cloud wave
  float passingCloud(vec2 p, float time) {
    float wave = 0.0;
    for (int i = 0; i < 8; i++) {
      if (i >= u_wave_count) break;
      float fi = float(i);
      float phase = fi * 1.618 + fi * 0.7;
      vec2 dir = normalize(u_wave_direction + vec2(sin(phase), cos(phase)) * u_turbulence);
      float freq = 2.0 + fi * 0.8;
      float speed = u_wave_speed * (1.0 + fi * 0.3) * (0.5 + u_arousal);
      wave += sin(dot(p, dir) * freq - time * speed + phase) * (1.0 / float(u_wave_count));
    }
    return wave * 0.5 + 0.5;
  }
  
  // Focal point influence
  float focalInfluence(vec2 p) {
    float influence = 0.0;
    for (int i = 0; i < 6; i++) {
      if (i >= u_focal_count) break;
      vec2 fp = u_focals[i].xy;
      float intensity = u_focals[i].z;
      float d = distance(p, fp);
      float ripple = sin(d * 12.0 - u_time * (2.0 + u_arousal * 4.0)) * 0.5 + 0.5;
      float falloff = exp(-d * d * 8.0) * intensity;
      influence += ripple * falloff;
    }
    return influence;
  }
  
  // Iridescence — hue shift based on position and time
  vec3 iridescent(float t) {
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.0, 0.33, 0.67);
    return a + b * cos(6.28318 * (c * t + d));
  }
  
  void main() {
    vec2 uv = v_uv;
    float time = u_time;
    
    // Orientation-based UV distortion
    vec2 orientUV = uv;
    if (u_orientation == 0) { // toward — expand from center
      vec2 center = vec2(0.5);
      float expand = 1.0 + sin(time * 0.3) * 0.02 * u_arousal;
      orientUV = center + (uv - center) * expand;
    } else if (u_orientation == 1) { // away — contract toward center
      vec2 center = vec2(0.5);
      float contract = 1.0 - sin(time * 0.4) * 0.03 * u_arousal;
      orientUV = center + (uv - center) * contract;
    } else if (u_orientation == 2) { // lateral — drift sideways
      orientUV.x += sin(time * 0.2) * 0.02;
    }
    // still = no distortion
    
    // Base noise field
    float noiseScale = 3.0 + u_pattern_complexity * 8.0;
    vec2 noiseUV = orientUV * noiseScale + time * u_wave_speed * 0.1 * u_wave_direction;
    float baseNoise = fbm(noiseUV, 4);
    
    // Turbulence distortion
    vec2 turbUV = orientUV + u_turbulence * 0.3 * vec2(
      fbm(orientUV * 4.0 + time * 0.15, 3) - 0.5,
      fbm(orientUV * 4.0 + time * 0.15 + 100.0, 3) - 0.5
    );
    
    // Cell structure — the individual chromatophores
    float cellScale = 15.0 + u_pattern_complexity * 25.0;
    float globalPulse = sin(time * u_pulse_frequency * 3.14159) * 0.15 + 0.5;
    float expansion = globalPulse * (0.3 + u_arousal * 0.5);
    
    // Pattern mode shapes
    float patternValue = 0.5;
    
    if (u_pattern_mode == 0) { // uniform
      patternValue = 0.4 + baseNoise * 0.15;
    } else if (u_pattern_mode == 1) { // mottled
      float mottleNoise = fbm(turbUV * (4.0 + u_pattern_complexity * 6.0) + time * 0.05, 5);
      patternValue = mottleNoise;
    } else if (u_pattern_mode == 2) { // disruptive
      float disrupt = fbm(turbUV * 3.0, 3);
      patternValue = step(0.45, disrupt); // hard edges
      patternValue = mix(patternValue, fbm(turbUV * 8.0, 4), 0.2); // slight detail
    } else if (u_pattern_mode == 3) { // passing_cloud
      patternValue = passingCloud(turbUV, time);
      // Layer with cell-level detail
      float cellDetail = chromatophoreCell(turbUV, cellScale * 0.5, expansion);
      patternValue = mix(patternValue, patternValue * (0.7 + cellDetail * 0.3), u_pattern_complexity);
    } else if (u_pattern_mode == 4) { // deimatic
      float flash = pow(sin(time * (3.0 + u_arousal * 8.0)) * 0.5 + 0.5, 3.0);
      float rings = 1.0 - smoothstep(0.1, 0.35, distance(uv, vec2(0.5)));
      float spotNoise = fbm(turbUV * 6.0 + time * 2.0, 3);
      patternValue = mix(spotNoise, flash * rings + spotNoise * 0.5, 0.6);
    }
    
    // Add focal point influence
    float focal = focalInfluence(uv);
    patternValue = mix(patternValue, patternValue + focal * 0.4, min(focal * 2.0, 1.0));
    
    // Add cell structure overlay
    float cells = chromatophoreCell(turbUV, cellScale, expansion);
    patternValue = mix(patternValue, patternValue * (0.6 + cells * 0.6), 0.4 + u_pattern_complexity * 0.4);
    
    patternValue = clamp(patternValue, 0.0, 1.0);
    
    // === COLOR COMPUTATION ===
    
    // Melanophore layer (darkness)
    float melanophore = u_darkness * (0.7 + patternValue * 0.3);
    
    // Warm palette (erythrophores + xanthophores)
    vec3 warmColor = mix(
      vec3(0.6, 0.15, 0.05),  // deep red-brown
      vec3(0.95, 0.65, 0.15), // amber-gold
      patternValue
    );
    
    // Cool palette (contracted/withdrawn)
    vec3 coolColor = mix(
      vec3(0.08, 0.06, 0.12), // deep blue-black
      vec3(0.25, 0.35, 0.45), // steel blue-grey
      patternValue * 0.6
    );
    
    // Blend warm/cool by warmth parameter
    vec3 pigmentColor = mix(coolColor, warmColor, u_warmth);
    
    // Apply melanophore darkness
    pigmentColor = mix(pigmentColor, vec3(0.02, 0.01, 0.03), melanophore * (1.0 - patternValue));
    
    // Brightness (xanthophore highlights)
    vec3 highlight = vec3(0.95, 0.85, 0.55);
    float highlightMask = pow(patternValue, 2.0) * u_brightness;
    pigmentColor = mix(pigmentColor, highlight, highlightMask * 0.5);
    
    // Iridophore layer — structural colour
    float iriAngle = dot(uv - 0.5, vec2(cos(time * 0.2), sin(time * 0.2)));
    float iriShift = iriAngle * 2.0 + time * 0.1 + fbm(turbUV * 3.0, 2) * 0.5;
    vec3 iriColor = iridescent(iriShift);
    pigmentColor = mix(pigmentColor, iriColor, u_iridescence * 0.35 * (0.5 + patternValue * 0.5));
    
    // Texture (papillae) — simulated as luminance variation
    float texNoise = fbm(orientUV * 30.0 + time * 0.02, 3);
    float texEffect = (texNoise - 0.5) * u_texture_intensity * 0.3;
    pigmentColor += texEffect;
    
    // Vignette
    float vignette = 1.0 - smoothstep(0.4, 0.85, distance(uv, vec2(0.5)) * 1.2);
    pigmentColor *= vignette;
    
    // Subtle film grain for organic quality
    float grain = (hash(uv * 1000.0 + time * 100.0) - 0.5) * 0.03;
    pigmentColor += grain;
    
    pigmentColor = clamp(pigmentColor, 0.0, 1.0);
    
    gl_FragColor = vec4(pigmentColor, 1.0);
  }
`;

const PATTERN_MODES = { uniform: 0, mottled: 1, disruptive: 2, passing_cloud: 3, deimatic: 4 };
const ORIENTATIONS = { toward: 0, away: 1, lateral: 2, still: 3 };

function createShader(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    console.error(gl.getShaderInfoLog(shader));
    gl.deleteShader(shader);
    return null;
  }
  return shader;
}

function createProgram(gl, vs, fs) {
  const program = gl.createProgram();
  gl.attachShader(program, vs);
  gl.attachShader(program, fs);
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    console.error(gl.getProgramInfoLog(program));
    return null;
  }
  return program;
}

export default function ChromatophoreDisplay() {
  const canvasRef = useRef(null);
  const glRef = useRef(null);
  const programRef = useRef(null);
  const uniformsRef = useRef({});
  const animRef = useRef(null);
  const startTimeRef = useRef(Date.now());
  const [activePreset, setActivePreset] = useState("navigable");
  const [showUI, setShowUI] = useState(true);
  const currentParams = useRef(PRESETS.navigable.params);
  const targetParams = useRef(PRESETS.navigable.params);
  const lerpSpeed = 0.02;

  const initGL = useCallback((canvas) => {
    const gl = canvas.getContext("webgl", { antialias: true, alpha: false });
    if (!gl) return;
    glRef.current = gl;

    const vs = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
    const fs = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);
    const program = createProgram(gl, vs, fs);
    programRef.current = program;
    gl.useProgram(program);

    // Fullscreen quad
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
    const posLoc = gl.getAttribLocation(program, "a_position");
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    // Cache uniform locations
    const names = [
      "u_time","u_arousal","u_valence","u_darkness","u_warmth","u_brightness",
      "u_iridescence","u_wave_speed","u_wave_count","u_wave_direction",
      "u_pulse_frequency","u_turbulence","u_pattern_complexity","u_texture_intensity",
      "u_pattern_mode","u_orientation","u_focal_count"
    ];
    const u = {};
    names.forEach(n => u[n] = gl.getUniformLocation(program, n));
    for (let i = 0; i < 6; i++) u[`u_focals[${i}]`] = gl.getUniformLocation(program, `u_focals[${i}]`);
    uniformsRef.current = u;
  }, []);

  function lerp(a, b, t) { return a + (b - a) * t; }

  function lerpParams(current, target, t) {
    return {
      ...target,
      arousal: lerp(current.arousal, target.arousal, t),
      valence: lerp(current.valence, target.valence, t),
      pattern_complexity: lerp(current.pattern_complexity, target.pattern_complexity, t),
      texture_intensity: lerp(current.texture_intensity, target.texture_intensity, t),
      palette: {
        darkness: lerp(current.palette.darkness, target.palette.darkness, t),
        warmth: lerp(current.palette.warmth, target.palette.warmth, t),
        brightness: lerp(current.palette.brightness, target.palette.brightness, t),
        iridescence: lerp(current.palette.iridescence, target.palette.iridescence, t),
      },
      dynamics: {
        ...target.dynamics,
        wave_speed: lerp(current.dynamics.wave_speed, target.dynamics.wave_speed, t),
        pulse_frequency: lerp(current.dynamics.pulse_frequency, target.dynamics.pulse_frequency, t),
        turbulence: lerp(current.dynamics.turbulence, target.dynamics.turbulence, t),
        wave_direction: [
          lerp(current.dynamics.wave_direction[0], target.dynamics.wave_direction[0], t),
          lerp(current.dynamics.wave_direction[1], target.dynamics.wave_direction[1], t),
        ],
      },
    };
  }

  const render = useCallback(() => {
    const gl = glRef.current;
    const program = programRef.current;
    const u = uniformsRef.current;
    if (!gl || !program) return;

    // Lerp current toward target
    currentParams.current = lerpParams(currentParams.current, targetParams.current, lerpSpeed);
    const p = currentParams.current;

    const canvas = canvasRef.current;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = canvas.clientWidth * dpr;
    const h = canvas.clientHeight * dpr;
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
      gl.viewport(0, 0, w, h);
    }

    const time = (Date.now() - startTimeRef.current) / 1000;
    gl.uniform1f(u.u_time, time);
    gl.uniform1f(u.u_arousal, p.arousal);
    gl.uniform1f(u.u_valence, p.valence);
    gl.uniform1f(u.u_darkness, p.palette.darkness);
    gl.uniform1f(u.u_warmth, p.palette.warmth);
    gl.uniform1f(u.u_brightness, p.palette.brightness);
    gl.uniform1f(u.u_iridescence, p.palette.iridescence);
    gl.uniform1f(u.u_wave_speed, p.dynamics.wave_speed);
    gl.uniform1i(u.u_wave_count, p.dynamics.wave_count);
    gl.uniform2f(u.u_wave_direction, p.dynamics.wave_direction[0], p.dynamics.wave_direction[1]);
    gl.uniform1f(u.u_pulse_frequency, p.dynamics.pulse_frequency);
    gl.uniform1f(u.u_turbulence, p.dynamics.turbulence);
    gl.uniform1f(u.u_pattern_complexity, p.pattern_complexity);
    gl.uniform1f(u.u_texture_intensity, p.texture_intensity);
    gl.uniform1i(u.u_pattern_mode, PATTERN_MODES[p.pattern_mode] ?? 1);
    gl.uniform1i(u.u_orientation, ORIENTATIONS[p.orientation] ?? 3);

    const focals = p.focal_points || [];
    gl.uniform1i(u.u_focal_count, Math.min(focals.length, 6));
    for (let i = 0; i < 6; i++) {
      const loc = u[`u_focals[${i}]`];
      if (i < focals.length) {
        gl.uniform3f(loc, focals[i].x, focals[i].y, focals[i].intensity);
      } else {
        gl.uniform3f(loc, 0, 0, 0);
      }
    }

    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    animRef.current = requestAnimationFrame(render);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    initGL(canvas);
    animRef.current = requestAnimationFrame(render);
    return () => { if (animRef.current) cancelAnimationFrame(animRef.current); };
  }, [initGL, render]);

  function selectPreset(key) {
    setActivePreset(key);
    targetParams.current = PRESETS[key].params;
  }

  return (
    <div style={{ position: "relative", width: "100%", height: "100vh", background: "#000", overflow: "hidden" }}>
      <canvas
        ref={canvasRef}
        style={{ width: "100%", height: "100%", display: "block", cursor: "crosshair" }}
        onClick={() => setShowUI(!showUI)}
      />

      {showUI && (
        <div style={{
          position: "absolute", bottom: 0, left: 0, right: 0,
          background: "linear-gradient(transparent, rgba(0,0,0,0.85) 30%)",
          padding: "48px 24px 24px",
        }}>
          <div style={{
            fontFamily: "'Cormorant Garamond', Georgia, serif",
            color: "rgba(255,255,255,0.5)",
            fontSize: "11px",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            marginBottom: "12px",
          }}>
            Chromatophore Display — tap canvas to toggle UI
          </div>

          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
            {Object.entries(PRESETS).map(([key, preset]) => (
              <button
                key={key}
                onClick={() => selectPreset(key)}
                style={{
                  padding: "8px 16px",
                  background: activePreset === key ? "rgba(255,255,255,0.15)" : "rgba(255,255,255,0.05)",
                  border: activePreset === key ? "1px solid rgba(255,255,255,0.4)" : "1px solid rgba(255,255,255,0.12)",
                  borderRadius: "4px",
                  color: activePreset === key ? "rgba(255,255,255,0.9)" : "rgba(255,255,255,0.5)",
                  fontFamily: "'DM Sans', system-ui, sans-serif",
                  fontSize: "12px",
                  cursor: "pointer",
                  transition: "all 0.3s ease",
                }}
              >
                {preset.label}
              </button>
            ))}
          </div>

          <div style={{
            fontFamily: "'DM Sans', system-ui, sans-serif",
            color: "rgba(255,255,255,0.4)",
            fontSize: "11px",
            marginTop: "8px",
          }}>
            {PRESETS[activePreset].desc}
          </div>

          <div style={{
            fontFamily: "'DM Sans', system-ui, sans-serif",
            color: "rgba(255,255,255,0.25)",
            fontSize: "10px",
            marginTop: "12px",
            lineHeight: 1.5,
          }}>
            orientation: {PRESETS[activePreset].params.orientation} · 
            arousal: {PRESETS[activePreset].params.arousal} · 
            valence: {PRESETS[activePreset].params.valence} · 
            pattern: {PRESETS[activePreset].params.pattern_mode} · 
            waves: {PRESETS[activePreset].params.dynamics.wave_count} · 
            focal points: {PRESETS[activePreset].params.focal_points.length}
          </div>
        </div>
      )}
    </div>
  );
}
