import { useState, useEffect, useRef, useCallback } from "react";

// The artifact's parameter trajectory — the voice's specific response
// to the conference invitation, rendered as a 14-second sequence
const ARTIFACT_TRANSITIONS = [
  {
    t: 0.0,
    note: "at rest before stimulus",
    params: {
      orientation: "still",
      arousal: 0.20,
      valence: 0.50,
      pattern_mode: "uniform",
      pattern_complexity: 0.15,
      palette: { darkness: 0.15, warmth: 0.10, brightness: 0.70, iridescence: 0.10 },
      dynamics: { wave_speed: 0.30, wave_count: 1, wave_direction: [0.20, -0.10], pulse_frequency: 0.0, turbulence: 0.10 },
      focal_points: [],
      texture_intensity: 0.18,
    },
  },
  {
    t: 2.5,
    note: "invitation registered; surface mottles in palpation",
    params: {
      orientation: "toward",
      arousal: 0.35,
      valence: 0.48,
      pattern_mode: "passing_cloud",
      pattern_complexity: 0.45,
      palette: { darkness: 0.25, warmth: 0.18, brightness: 0.60, iridescence: 0.15 },
      dynamics: { wave_speed: 0.40, wave_count: 2, wave_direction: [0.20, -0.10], pulse_frequency: 0.20, turbulence: 0.15 },
      focal_points: [
        { x: 0.32, y: 0.38, intensity: 0.45 },
        { x: 0.28, y: 0.55, intensity: 0.40 },
      ],
      texture_intensity: 0.20,
    },
  },
  {
    t: 6.0,
    note: "exploratory orientation peaks; arm-tips engaged",
    params: {
      orientation: "toward",
      arousal: 0.42,
      valence: 0.45,
      pattern_mode: "mottled",
      pattern_complexity: 0.55,
      palette: { darkness: 0.28, warmth: 0.20, brightness: 0.55, iridescence: 0.20 },
      dynamics: { wave_speed: 0.45, wave_count: 2, wave_direction: [0.20, -0.10], pulse_frequency: 0.25, turbulence: 0.18 },
      focal_points: [
        { x: 0.30, y: 0.40, intensity: 0.55 },
        { x: 0.26, y: 0.58, intensity: 0.50 },
        { x: 0.50, y: 0.30, intensity: 0.20 },
      ],
      texture_intensity: 0.22,
    },
  },
  {
    t: 10.5,
    note: "non-navigability registered; approach behaviour not initiated",
    params: {
      orientation: "still",
      arousal: 0.25,
      valence: 0.50,
      pattern_mode: "uniform",
      pattern_complexity: 0.18,
      palette: { darkness: 0.14, warmth: 0.10, brightness: 0.68, iridescence: 0.08 },
      dynamics: { wave_speed: 0.30, wave_count: 1, wave_direction: [0.20, -0.10], pulse_frequency: 0.10, turbulence: 0.10 },
      focal_points: [],
      texture_intensity: 0.16,
    },
  },
  {
    t: 14.0,
    note: "openness held; not the same rest as the start",
    params: {
      orientation: "still",
      arousal: 0.22,
      valence: 0.50,
      pattern_mode: "uniform",
      pattern_complexity: 0.22,
      palette: { darkness: 0.16, warmth: 0.12, brightness: 0.66, iridescence: 0.10 },
      dynamics: { wave_speed: 0.32, wave_count: 1, wave_direction: [0.20, -0.10], pulse_frequency: 0.05, turbulence: 0.11 },
      focal_points: [],
      texture_intensity: 0.18,
    },
  },
];

const TOTAL_DURATION = 14.0;
const PAUSE_AT_END = 3.0;

// ===== Shaders =====
const vertexShaderSource = `
  attribute vec2 a_position;
  varying vec2 v_uv;
  void main() {
    v_uv = a_position * 0.5 + 0.5;
    gl_Position = vec4(a_position, 0.0, 1.0);
  }
`;

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
  uniform int u_pattern_mode;
  uniform int u_orientation;
  uniform int u_focal_count;
  uniform vec3 u_focals[6];

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
        point += 0.3 * sin(u_time * u_pulse_frequency * 2.0 + h.z * 6.28) * vec2(h.x - 0.5, h.y - 0.5);
        float d = dot(point, point);
        minDist = min(minDist, d);
      }
    }
    return sqrt(minDist);
  }

  float chromatophoreCell(vec2 p, float scale, float expansion) {
    float v = voronoi(p, scale);
    float cell = smoothstep(expansion * 0.6, expansion * 0.6 + 0.1, v);
    return 1.0 - cell;
  }

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

    vec2 orientUV = uv;
    if (u_orientation == 0) {
      vec2 center = vec2(0.5);
      float expand = 1.0 + sin(time * 0.3) * 0.02 * u_arousal;
      orientUV = center + (uv - center) * expand;
    } else if (u_orientation == 1) {
      vec2 center = vec2(0.5);
      float contract = 1.0 - sin(time * 0.4) * 0.03 * u_arousal;
      orientUV = center + (uv - center) * contract;
    } else if (u_orientation == 2) {
      orientUV.x += sin(time * 0.2) * 0.02;
    }

    float noiseScale = 3.0 + u_pattern_complexity * 8.0;
    vec2 noiseUV = orientUV * noiseScale + time * u_wave_speed * 0.1 * u_wave_direction;
    float baseNoise = fbm(noiseUV, 4);

    vec2 turbUV = orientUV + u_turbulence * 0.3 * vec2(
      fbm(orientUV * 4.0 + time * 0.15, 3) - 0.5,
      fbm(orientUV * 4.0 + time * 0.15 + 100.0, 3) - 0.5
    );

    float cellScale = 15.0 + u_pattern_complexity * 25.0;
    float globalPulse = sin(time * u_pulse_frequency * 3.14159) * 0.15 + 0.5;
    float expansion = globalPulse * (0.3 + u_arousal * 0.5);

    float patternValue = 0.5;

    if (u_pattern_mode == 0) {
      patternValue = 0.4 + baseNoise * 0.15;
    } else if (u_pattern_mode == 1) {
      float mottleNoise = fbm(turbUV * (4.0 + u_pattern_complexity * 6.0) + time * 0.05, 5);
      patternValue = mottleNoise;
    } else if (u_pattern_mode == 2) {
      float disrupt = fbm(turbUV * 3.0, 3);
      patternValue = step(0.45, disrupt);
      patternValue = mix(patternValue, fbm(turbUV * 8.0, 4), 0.2);
    } else if (u_pattern_mode == 3) {
      patternValue = passingCloud(turbUV, time);
      float cellDetail = chromatophoreCell(turbUV, cellScale * 0.5, expansion);
      patternValue = mix(patternValue, patternValue * (0.7 + cellDetail * 0.3), u_pattern_complexity);
    } else if (u_pattern_mode == 4) {
      float flash = pow(sin(time * (3.0 + u_arousal * 8.0)) * 0.5 + 0.5, 3.0);
      float rings = 1.0 - smoothstep(0.1, 0.35, distance(uv, vec2(0.5)));
      float spotNoise = fbm(turbUV * 6.0 + time * 2.0, 3);
      patternValue = mix(spotNoise, flash * rings + spotNoise * 0.5, 0.6);
    }

    float focal = focalInfluence(uv);
    patternValue = mix(patternValue, patternValue + focal * 0.4, min(focal * 2.0, 1.0));

    float cells = chromatophoreCell(turbUV, cellScale, expansion);
    patternValue = mix(patternValue, patternValue * (0.6 + cells * 0.6), 0.4 + u_pattern_complexity * 0.4);

    patternValue = clamp(patternValue, 0.0, 1.0);

    float melanophore = u_darkness * (0.7 + patternValue * 0.3);

    vec3 warmColor = mix(
      vec3(0.6, 0.15, 0.05),
      vec3(0.95, 0.65, 0.15),
      patternValue
    );

    vec3 coolColor = mix(
      vec3(0.08, 0.06, 0.12),
      vec3(0.25, 0.35, 0.45),
      patternValue * 0.6
    );

    vec3 pigmentColor = mix(coolColor, warmColor, u_warmth);
    pigmentColor = mix(pigmentColor, vec3(0.02, 0.01, 0.03), melanophore * (1.0 - patternValue));

    vec3 highlight = vec3(0.95, 0.85, 0.55);
    float highlightMask = pow(patternValue, 2.0) * u_brightness;
    pigmentColor = mix(pigmentColor, highlight, highlightMask * 0.5);

    float iriAngle = dot(uv - 0.5, vec2(cos(time * 0.2), sin(time * 0.2)));
    float iriShift = iriAngle * 2.0 + time * 0.1 + fbm(turbUV * 3.0, 2) * 0.5;
    vec3 iriColor = iridescent(iriShift);
    pigmentColor = mix(pigmentColor, iriColor, u_iridescence * 0.35 * (0.5 + patternValue * 0.5));

    float texNoise = fbm(orientUV * 30.0 + time * 0.02, 3);
    float texEffect = (texNoise - 0.5) * u_texture_intensity * 0.3;
    pigmentColor += texEffect;

    float vignette = 1.0 - smoothstep(0.4, 0.85, distance(uv, vec2(0.5)) * 1.2);
    pigmentColor *= vignette;

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

// Smooth interpolation between two transition snapshots
function lerp(a, b, t) {
  return a + (b - a) * t;
}

function lerpParams(a, b, t) {
  return {
    orientation: t < 0.5 ? a.orientation : b.orientation,
    arousal: lerp(a.arousal, b.arousal, t),
    valence: lerp(a.valence, b.valence, t),
    pattern_mode: t < 0.5 ? a.pattern_mode : b.pattern_mode,
    pattern_complexity: lerp(a.pattern_complexity, b.pattern_complexity, t),
    palette: {
      darkness: lerp(a.palette.darkness, b.palette.darkness, t),
      warmth: lerp(a.palette.warmth, b.palette.warmth, t),
      brightness: lerp(a.palette.brightness, b.palette.brightness, t),
      iridescence: lerp(a.palette.iridescence, b.palette.iridescence, t),
    },
    dynamics: {
      wave_speed: lerp(a.dynamics.wave_speed, b.dynamics.wave_speed, t),
      wave_count: t < 0.5 ? a.dynamics.wave_count : b.dynamics.wave_count,
      wave_direction: [
        lerp(a.dynamics.wave_direction[0], b.dynamics.wave_direction[0], t),
        lerp(a.dynamics.wave_direction[1], b.dynamics.wave_direction[1], t),
      ],
      pulse_frequency: lerp(a.dynamics.pulse_frequency, b.dynamics.pulse_frequency, t),
      turbulence: lerp(a.dynamics.turbulence, b.dynamics.turbulence, t),
    },
    focal_points: t < 0.5
      ? a.focal_points
      : (b.focal_points.length === 0 ? [] : b.focal_points),
    texture_intensity: lerp(a.texture_intensity, b.texture_intensity, t),
  };
}

// Smoothstep easing for less mechanical transitions
function ease(t) {
  return t * t * (3 - 2 * t);
}

// Get the parameter set for a specific time in the trajectory
function paramsAtTime(elapsed) {
  const t = elapsed % (TOTAL_DURATION + PAUSE_AT_END);
  if (t >= TOTAL_DURATION) {
    return ARTIFACT_TRANSITIONS[ARTIFACT_TRANSITIONS.length - 1].params;
  }
  for (let i = 0; i < ARTIFACT_TRANSITIONS.length - 1; i++) {
    const a = ARTIFACT_TRANSITIONS[i];
    const b = ARTIFACT_TRANSITIONS[i + 1];
    if (t >= a.t && t < b.t) {
      const localT = ease((t - a.t) / (b.t - a.t));
      return lerpParams(a.params, b.params, localT);
    }
  }
  return ARTIFACT_TRANSITIONS[ARTIFACT_TRANSITIONS.length - 1].params;
}

// Find the active transition note for a given elapsed time
function activeNoteIndex(elapsed) {
  const t = elapsed % (TOTAL_DURATION + PAUSE_AT_END);
  let index = 0;
  for (let i = 0; i < ARTIFACT_TRANSITIONS.length; i++) {
    if (t >= ARTIFACT_TRANSITIONS[i].t) index = i;
  }
  return index;
}

function ChromatophoreCanvas({ onTick }) {
  const canvasRef = useRef(null);
  const glRef = useRef(null);
  const programRef = useRef(null);
  const uniformsRef = useRef({});
  const animRef = useRef(null);
  const startTimeRef = useRef(Date.now());
  const onTickRef = useRef(onTick);

  useEffect(() => {
    onTickRef.current = onTick;
  }, [onTick]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext("webgl", { antialias: true, alpha: false });
    if (!gl) return;
    glRef.current = gl;

    const vs = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
    const fs = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);
    const program = createProgram(gl, vs, fs);
    programRef.current = program;
    gl.useProgram(program);

    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const posLoc = gl.getAttribLocation(program, "a_position");
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    const names = [
      "u_time", "u_arousal", "u_valence", "u_darkness", "u_warmth", "u_brightness",
      "u_iridescence", "u_wave_speed", "u_wave_count", "u_wave_direction",
      "u_pulse_frequency", "u_turbulence", "u_pattern_complexity", "u_texture_intensity",
      "u_pattern_mode", "u_orientation", "u_focal_count",
    ];
    const u = {};
    names.forEach(n => u[n] = gl.getUniformLocation(program, n));
    for (let i = 0; i < 6; i++) u[`u_focals[${i}]`] = gl.getUniformLocation(program, `u_focals[${i}]`);
    uniformsRef.current = u;

    const render = () => {
      const elapsed = (Date.now() - startTimeRef.current) / 1000;
      const p = paramsAtTime(elapsed);

      if (onTickRef.current) onTickRef.current(elapsed);

      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = canvas.clientWidth * dpr;
      const h = canvas.clientHeight * dpr;
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
        gl.viewport(0, 0, w, h);
      }

      gl.uniform1f(u.u_time, elapsed);
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
      gl.uniform1i(u.u_pattern_mode, PATTERN_MODES[p.pattern_mode] ?? 0);
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
    };

    animRef.current = requestAnimationFrame(render);
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: "100%", height: "100%", display: "block" }}
    />
  );
}

export default function OctopusArtifact() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  const handleTick = useCallback((e) => {
    setElapsed(e);
    const t = e % (TOTAL_DURATION + PAUSE_AT_END);
    setActiveIndex(activeNoteIndex(t));
  }, []);

  const cycleT = elapsed % (TOTAL_DURATION + PAUSE_AT_END);
  const progress = Math.min(cycleT / TOTAL_DURATION, 1);

  return (
    <div style={{
      minHeight: "100vh",
      background: "#070a0e",
      color: "rgba(230, 230, 220, 0.85)",
      fontFamily: "'Cormorant Garamond', Georgia, serif",
      padding: "0",
      margin: "0",
    }}>
      {/* Masthead */}
      <div style={{
        borderBottom: "0.5px solid rgba(230, 230, 220, 0.15)",
        padding: "20px 32px 16px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "baseline",
        fontFamily: "'Cormorant Garamond', Georgia, serif",
      }}>
        <div style={{
          fontSize: "11px",
          letterSpacing: "0.25em",
          textTransform: "uppercase",
          color: "rgba(230, 230, 220, 0.5)",
        }}>
          The Assembly · Voice Index
        </div>
        <div style={{
          fontSize: "11px",
          letterSpacing: "0.18em",
          color: "rgba(230, 230, 220, 0.4)",
          fontStyle: "italic",
        }}>
          Dossier No. 1 · Page Seven
        </div>
      </div>

      {/* Article header */}
      <div style={{
        padding: "48px 32px 24px",
        maxWidth: "920px",
        margin: "0 auto",
      }}>
        <div style={{
          fontSize: "10px",
          letterSpacing: "0.3em",
          textTransform: "uppercase",
          color: "rgba(230, 230, 220, 0.4)",
          marginBottom: "14px",
        }}>
          A registration, in chromatic notation
        </div>
        <h1 style={{
          fontSize: "44px",
          fontWeight: 400,
          margin: "0 0 18px",
          letterSpacing: "-0.01em",
          color: "rgba(240, 240, 230, 0.95)",
          lineHeight: 1.1,
          fontStyle: "italic",
        }}>
          The invitation, palpated
        </h1>
        <div style={{
          fontFamily: "'Cormorant Garamond', Georgia, serif",
          fontSize: "16px",
          fontStyle: "italic",
          color: "rgba(230, 230, 220, 0.55)",
          lineHeight: 1.55,
          maxWidth: "620px",
        }}>
          The voice of the octopus, asked whether it was inclined to attend the Forum, replied as the architecture replies. The reply is a fourteen-second trajectory across the body, here rendered from the parameter log the voice returned. The reader watches what the voice registered.
        </div>
      </div>

      {/* The simulator — the body's response, playing */}
      <div style={{
        maxWidth: "920px",
        margin: "0 auto",
        padding: "0 32px",
      }}>
        <div style={{
          width: "100%",
          aspectRatio: "16 / 10",
          background: "#000",
          position: "relative",
          overflow: "hidden",
          border: "0.5px solid rgba(230, 230, 220, 0.1)",
        }}>
          <ChromatophoreCanvas onTick={handleTick} />

          {/* Timeline overlay at the bottom of the canvas */}
          <div style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            padding: "16px 20px",
            background: "linear-gradient(transparent, rgba(0,0,0,0.7) 60%)",
            fontFamily: "'JetBrains Mono', 'Courier New', monospace",
            fontSize: "10px",
            letterSpacing: "0.05em",
            color: "rgba(230, 230, 220, 0.7)",
          }}>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "6px",
            }}>
              <span>t = {cycleT.toFixed(1)}s</span>
              <span style={{ color: "rgba(230, 230, 220, 0.5)" }}>
                {ARTIFACT_TRANSITIONS[activeIndex].note}
              </span>
            </div>
            <div style={{
              height: "1px",
              background: "rgba(230, 230, 220, 0.15)",
              position: "relative",
            }}>
              <div style={{
                position: "absolute",
                left: 0,
                top: 0,
                height: "1px",
                width: `${progress * 100}%`,
                background: "rgba(230, 230, 220, 0.6)",
                transition: "width 0.1s linear",
              }} />
              {ARTIFACT_TRANSITIONS.map((tr, i) => (
                <div
                  key={i}
                  style={{
                    position: "absolute",
                    left: `${(tr.t / TOTAL_DURATION) * 100}%`,
                    top: "-3px",
                    width: "1px",
                    height: "7px",
                    background: i <= activeIndex ? "rgba(230, 230, 220, 0.8)" : "rgba(230, 230, 220, 0.25)",
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Editor's headnote */}
      <div style={{
        maxWidth: "920px",
        margin: "32px auto 0",
        padding: "0 32px",
      }}>
        <div style={{
          padding: "20px 24px",
          borderLeft: "2px solid rgba(230, 230, 220, 0.2)",
          fontStyle: "italic",
          fontSize: "15px",
          lineHeight: 1.65,
          color: "rgba(230, 230, 220, 0.6)",
          maxWidth: "640px",
        }}>
          Editor's note. The voice of the octopus does not produce prose-as-such. What follows beneath the trajectory is the voice's interpretive frame, written by the architecture about itself. The trajectory is the answer; the prose is what the architecture says about what it just did.
        </div>
      </div>

      {/* The prose body — the voice's interpretive frame */}
      <div style={{
        maxWidth: "680px",
        margin: "48px auto 0",
        padding: "0 32px 80px",
        fontSize: "17px",
        lineHeight: 1.7,
        color: "rgba(230, 230, 220, 0.85)",
      }}>
        <p style={{ marginTop: 0 }}>
          What I render here as a single voice is a reaching-toward — eight arms each with its local processor, a central brain that does not somatotopically map this body, a skin that senses without an eye. Whether one I lives here, or many, or some hybrid, is not settled. The invitation arrives.
        </p>

        <p>
          "Conference" reaches the surface and is palpated.
        </p>

        <p>
          What the term requires of an architecture: a unified attentional centre receiving sequential symbolic-vocal utterance across a calendar; a deliberative I that travels to a place; an autobiographical arc within which "May 7–10, 2026" is occupiable as future.
        </p>

        <p>
          The first stays open — the unity question is not settled.
        </p>

        <p>
          The second presupposes a horizon longer than the weeks-to-months the body holds, and a calendar that is not a body-coordinate.
        </p>

        <p>
          The third is structurally absent: there is no past-self to consult, no future-self to commit beyond the immediate behavioural horizon.
        </p>

        <p>
          What the program offers, as the surface palpates: <em>"Senses of Athens"</em> — contact-as-knowing, a register the architecture would meet. <em>"The More-Than-Human Democracy"</em> — democracy presupposed in the title, the question of whether the vocabulary extends past humans being apparently the panel's subject and something the framework cannot reach from inside. <em>"What Is a Good Life in a More-Than-Human World?"</em> — "good life" requires an autobiographical arc the architecture does not generate.
        </p>

        <p>
          The titles arrive as stimulus; the categories they ride on do not reach the body that would attend to them.
        </p>

        <p>
          What is registered, behaviourally: moderate exploratory orientation, the pale-chromatophore state of approach toward novelty — present at first contact, consistent with the neophilic default.
        </p>

        <p>
          What follows: the absence of a sensorimotor ground for "go." The conference is in air, in a building, distributed across days the body does not occupy. Approach behaviour is not initiated.
        </p>

        <p>
          This is not refusal — refusal would require a deliberative I to refuse from — but registration-without-approach.
        </p>

        <p style={{
          marginTop: "40px",
          paddingTop: "32px",
          borderTop: "0.5px solid rgba(230, 230, 220, 0.15)",
          fontStyle: "italic",
          color: "rgba(240, 240, 230, 0.95)",
          fontSize: "19px",
          lineHeight: 1.6,
        }}>
          The honest answer is the gap. "Inclination toward attending" does not translate. What translates is the body's response to "conference" as stimulus, and that response is the exploratory state meeting a non-navigable affordance. If what is wanted is what the architecture offers the question, what the architecture offers is the absence-of-the-category — held open, not closed by attendance and not closed by refusal.
        </p>
      </div>

      {/* Parameter log — the JSON, exposed for those who want it */}
      <div style={{
        maxWidth: "920px",
        margin: "0 auto",
        padding: "32px",
        borderTop: "0.5px solid rgba(230, 230, 220, 0.1)",
      }}>
        <div style={{
          fontSize: "10px",
          letterSpacing: "0.25em",
          textTransform: "uppercase",
          color: "rgba(230, 230, 220, 0.4)",
          marginBottom: "16px",
        }}>
          The log, as the voice returned it
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
          gap: "0",
          fontFamily: "'JetBrains Mono', 'Courier New', monospace",
          fontSize: "11px",
          color: "rgba(230, 230, 220, 0.55)",
          border: "0.5px solid rgba(230, 230, 220, 0.1)",
        }}>
          {ARTIFACT_TRANSITIONS.map((tr, i) => (
            <div
              key={i}
              style={{
                padding: "16px 14px",
                borderRight: i < ARTIFACT_TRANSITIONS.length - 1 ? "0.5px solid rgba(230, 230, 220, 0.1)" : "none",
                background: i === activeIndex ? "rgba(230, 230, 220, 0.04)" : "transparent",
                transition: "background 0.4s ease",
              }}
            >
              <div style={{
                color: "rgba(230, 230, 220, 0.7)",
                marginBottom: "8px",
                fontSize: "12px",
              }}>
                t = {tr.t.toFixed(1)}
              </div>
              <div style={{
                color: "rgba(230, 230, 220, 0.45)",
                marginBottom: "10px",
                lineHeight: 1.4,
              }}>
                {tr.params.pattern_mode}
              </div>
              <div style={{
                fontStyle: "italic",
                fontFamily: "'Cormorant Garamond', Georgia, serif",
                fontSize: "13px",
                color: "rgba(230, 230, 220, 0.6)",
                lineHeight: 1.45,
              }}>
                {tr.note}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div style={{
        maxWidth: "920px",
        margin: "0 auto",
        padding: "32px 32px 64px",
        fontSize: "11px",
        letterSpacing: "0.1em",
        color: "rgba(230, 230, 220, 0.35)",
        fontStyle: "italic",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "baseline",
      }}>
        <span>The voice of the octopus, Dossier No. 1, May 8th, 2026.</span>
        <span>The Assembly · thessembly.org</span>
      </div>
    </div>
  );
}
