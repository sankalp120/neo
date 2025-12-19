import * as THREE from "three";
import { OrbitControls } from "jsm/controls/OrbitControls.js";

// --------------------
// READ DATE RANGE
// --------------------
const params = new URLSearchParams(window.location.search);
const startDate = params.get("start_date");
const endDate = params.get("end_date");

document.getElementById("dateInfo").textContent =
  `Date range: ${startDate} → ${endDate}`;

const API_URL =
  `http://127.0.0.1:8000/asteroids?start_date=${startDate}&end_date=${endDate}`;

// --------------------
// THREE SETUP
// --------------------
const w = window.innerWidth;
const h = window.innerHeight;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, w / h, 0.1, 1000);
camera.position.z = 40;

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(w, h);
document.body.appendChild(renderer.domElement);

new OrbitControls(camera, renderer.domElement);

// --------------------
// EARTH
// --------------------
const earthGroup = new THREE.Group();
earthGroup.rotation.z = -23.4 * Math.PI / 180;
scene.add(earthGroup);

const loader = new THREE.TextureLoader();
const geometry = new THREE.IcosahedronGeometry(1, 12);

const earthMesh = new THREE.Mesh(
  geometry,
  new THREE.MeshPhongMaterial({
    map: loader.load("./textures/Earth_Diffuse_6K.jpg"),
    specularMap: loader.load("./textures/Earth_Glossiness_6K.jpg"),
    bumpMap: loader.load("./textures/Earth_NormalNRM_6K.jpg"),
    bumpScale: 0.04,
  })
);
earthGroup.add(earthMesh);

// --------------------
// LIGHT
// --------------------
const sunLight = new THREE.DirectionalLight(0xffffff, 2);
sunLight.position.set(-2, 0.5, 1.5);
scene.add(sunLight);

// --------------------
// ASTEROIDS
// --------------------
const asteroidGroup = new THREE.Group();
scene.add(asteroidGroup);

function nasaLogDistance(km) {
  return Math.log10(Math.max(km, 1)) * 4;
}

function createAsteroidMesh(ast) {
  const distance = nasaLogDistance(ast.miss_distance_km);

  const theta = Math.random() * Math.PI * 2;
  const phi = Math.acos(2 * Math.random() - 1);

  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.3, 6, 6),
    new THREE.MeshStandardMaterial({
      color: ast.hazardous ? 0xff4444 : 0xaaaaaa
    })
  );

  mesh.position.set(
    distance * Math.sin(phi) * Math.cos(theta),
    distance * Math.sin(phi) * Math.sin(theta),
    distance * Math.cos(phi)
  );

  return mesh;
}

fetch(API_URL)
  .then(res => res.json())
  .then(data => {
    data.forEach(ast => asteroidGroup.add(createAsteroidMesh(ast)));
    console.log("Asteroids rendered:", asteroidGroup.children.length);
  });

function animate() {
  requestAnimationFrame(animate);
  earthMesh.rotation.y += 0.002;
  renderer.render(scene, camera);
  lightsMesh.rotation.y += 0.002;
  cloudsMesh.rotation.y += 0.0023;
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
