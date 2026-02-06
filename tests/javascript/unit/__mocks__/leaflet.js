// Mock for Leaflet library
// Based on react-leaflet's mock: https://github.com/PaulLeCam/react-leaflet/blob/master/__mocks__/leaflet.js

const leaflet = {
  // Map methods
  map: jest.fn((id, options) => ({
    setView: jest.fn().mockReturnThis(),
    addTo: jest.fn().mockReturnThis(),
    on: jest.fn().mockReturnThis(),
    off: jest.fn().mockReturnThis(),
    remove: jest.fn().mockReturnThis(),
    getCenter: jest.fn(() => ({ lat: 45.75, lng: 4.85 })),
    getZoom: jest.fn(() => 13),
    panTo: jest.fn().mockReturnThis(),
    fitBounds: jest.fn().mockReturnThis(),
    eachLayer: jest.fn(),
    removeLayer: jest.fn().mockReturnThis(),
    options: {},
  })),

  // Marker methods
  marker: jest.fn((latlng, options) => ({
    addTo: jest.fn().mockReturnThis(),
    on: jest.fn().mockReturnThis(),
    off: jest.fn().mockReturnThis(),
    bindPopup: jest.fn().mockReturnThis(),
    openPopup: jest.fn().mockReturnThis(),
    unbindPopup: jest.fn().mockReturnThis(),
    getPopup: jest.fn(() => null),
    getLatLng: jest.fn(() => latlng),
    setLatLng: jest.fn().mockReturnThis(),
    remove: jest.fn().mockReturnThis(),
    options: options || {},
    _popup: {},
  })),

  // Popup methods
  popup: jest.fn((options) => ({
    setContent: jest.fn().mockReturnThis(),
    setLatLng: jest.fn().mockReturnThis(),
    update: jest.fn().mockReturnThis(),
    isOpen: jest.fn(() => false),
    options: options || {},
  })),

  // Icon methods
  icon: jest.fn((options) => ({
    options: options || {},
  })),

  divIcon: jest.fn((options) => ({
    options: options || {},
    createIcon: jest.fn(),
    createShadow: jest.fn(),
  })),

  // LatLng and LatLngBounds
  latLng: jest.fn((lat, lng) => [lat, lng]),
  latLngBounds: jest.fn(() => ({
    extend: jest.fn().mockReturnThis(),
    isValid: jest.fn(() => true),
    getCenter: jest.fn(() => ({ lat: 45.75, lng: 4.85 })),
  })),

  // Tile layer
  tileLayer: jest.fn((url, options) => ({
    addTo: jest.fn().mockReturnThis(),
    remove: jest.fn().mockReturnThis(),
    options: options || {},
  })),

  // Control methods
  control: jest.fn(() => ({
    addTo: jest.fn().mockReturnThis(),
    remove: jest.fn().mockReturnThis(),
    getContainer: jest.fn(() => document.createElement('div')),
    options: {},
  })),

  // DOM utilities
  DomUtil: {
    create: jest.fn((tag, className) => document.createElement(tag)),
    get: jest.fn((id) => document.getElementById(id)),
    addClass: jest.fn(),
    removeClass: jest.fn(),
    setPosition: jest.fn(),
    getStyle: jest.fn(),
  },

  // DOM events
  DomEvent: {
    on: jest.fn((el, event, fn) => {
      el.addEventListener(event, fn);
      return { on: jest.fn().mockReturnThis() };
    }),
    off: jest.fn((el, event, fn) => {
      el.removeEventListener(event, fn);
      return { off: jest.fn().mockReturnThis() };
    }),
    stopPropagation: jest.fn((e) => e.stopPropagation()),
    preventDefault: jest.fn((e) => e.preventDefault()),
    stop: jest.fn((e) => {
      e.stopPropagation();
      e.preventDefault();
    }),
  },

  // Other utilities
  point: jest.fn((x, y) => [x, y]),
  bounds: jest.fn((a, b) => [a, b]),
  transform: jest.fn((point, matrix) => point),
  line: jest.fn((points) => points),
  polygon: jest.fn((points) => points),
  polyline: jest.fn((points) => points),
  circle: jest.fn((center, radius) => ({ center, radius })),
  circleMarker: jest.fn((center, options) => ({ center, options })),
  rectangle: jest.fn((bounds, options) => ({ bounds, options })),
  svg: jest.fn(() => ({})),
  canvas: jest.fn(() => ({})),
  path: jest.fn(() => ({})),
};

// Add version info
leaflet.version = '1.7.1';

module.exports = leaflet;