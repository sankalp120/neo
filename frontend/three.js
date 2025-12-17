import * as THREE from "three";
import { OrbitControls } from "jsm/controls/OrbitControls.js";

const w = window.innerWidth;
const h = window.innerHeight;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, w / h, 0.1, 1000);
camera.position.z = 5;
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(w, h);
document.body.appendChild(renderer.domElement);
// THREE.ColorManagement.enabled = true;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;

const earthGroup = new THREE.Group();
earthGroup.rotation.z = -23.4 * Math.PI / 180;
scene.add(earthGroup);
new OrbitControls(camera, renderer.domElement);
const detail = 12;
const loader = new THREE.TextureLoader();
const geometry = new THREE.IcosahedronGeometry(1, detail);
const material = new THREE.MeshPhongMaterial({
  map: loader.load("./textures/Earth_Diffuse_6K.jpg"),
  specularMap: loader.load("./textures/Earth_Glossiness_6K.jpg"),
  bumpMap: loader.load("./textures/Earth_NormalNRM_6K.jpg"),
  bumpScale: 0.04,
});
// material.map.colorSpace = THREE.SRGBColorSpace;
const earthMesh = new THREE.Mesh(geometry, material);
earthGroup.add(earthMesh);

const lightsMat = new THREE.MeshBasicMaterial({
  map: loader.load("./textures/Earth_Illumination_6K.jpg"),
  blending: THREE.AdditiveBlending,
});
const lightsMesh = new THREE.Mesh(geometry, lightsMat);
earthGroup.add(lightsMesh);

const cloudsMat = new THREE.MeshStandardMaterial({
  map: loader.load("./textures/Earth_Clouds_6K.jpg"),
  transparent: true,
  opacity: 0.8,
  blending: THREE.AdditiveBlending,
  //alphaMap: loader.load('./textures/05_earthcloudmaptrans.jpg'),
  // alphaTest: 0.3,
});
const cloudsMesh = new THREE.Mesh(geometry, cloudsMat);
cloudsMesh.scale.setScalar(1.003);
earthGroup.add(cloudsMesh);

// const fresnelMat = getFresnelMat();
// const glowMesh = new THREE.Mesh(geometry, fresnelMat);
// glowMesh.scale.setScalar(1.01);
// earthGroup.add(glowMesh);

// const stars = getStarfield({numStars: 2000});
// scene.add(stars);

const sunLight = new THREE.DirectionalLight(0xffffff, 2.0);
sunLight.position.set(-2, 0.5, 1.5);
scene.add(sunLight);

//

const asteroidGroup = new THREE.Group();
scene.add(asteroidGroup);

const API_URL =
  "http://127.0.0.1:8000/asteroids?start_date=2024-01-01&end_date=2024-01-03";

// NASA-style logarithmic distance (used by JPL)
function nasaLogDistance(km) {
  return Math.log10(Math.max(km, 1)) * 4;
}

function createAsteroidMesh(asteroid) {
  const distanceKm = Number(asteroid.miss_distance_km);
  const diameterM = Number(asteroid.diameter_m);

  // 🚨 HARD VALIDATION (keeps geometry sane)
  if (
    !Number.isFinite(distanceKm) ||
    !Number.isFinite(diameterM) ||
    distanceKm <= 0 ||
    diameterM <= 0
  ) {
    return null;
  }

  // Convert meters → km
  const diameterKm = diameterM / 1000;

  // NASA log-scaled distance
  const distance = nasaLogDistance(distanceKm);

  // Random direction (spherical distribution)
  const theta = Math.random() * Math.PI * 2;
  const phi = Math.acos(2 * Math.random() - 1);

  const x = distance * Math.sin(phi) * Math.cos(theta);
  const y = distance * Math.sin(phi) * Math.sin(theta);
  const z = distance * Math.cos(phi);

  // Size (log-scaled so small objects remain visible)
  //const radius = Math.max(Math.log10(diameterKm + 1) * 0.02, 0.02);
  const radius = .3;

  const geom = new THREE.SphereGeometry(radius, 6, 6);
  const mat = new THREE.MeshStandardMaterial({
    color: asteroid.hazardous ? 0xff4444 : 0xaaaaaa,
  });

  const mesh = new THREE.Mesh(geom, mat);
  mesh.position.set(x, y, z);

  return mesh;
}

fetch(API_URL)
  .then(res => res.json())
  .then(asteroids => {
    asteroids.forEach(ast => {
      const mesh = createAsteroidMesh(ast);
      if (mesh) asteroidGroup.add(mesh);
    });

    console.log("Asteroids rendered:", asteroidGroup.children.length);
  })
  .catch(err => console.error("Asteroid fetch failed:", err));


function animate() {
  requestAnimationFrame(animate);

  earthMesh.rotation.y += 0.002;
  lightsMesh.rotation.y += 0.002;
  cloudsMesh.rotation.y += 0.0023;
  // glowMesh.rotation.y += 0.002;
  // stars.rotation.y -= 0.0002;
  renderer.render(scene, camera);
}
animate();
function handleWindowResize () {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}
window.addEventListener('resize', handleWindowResize, false);