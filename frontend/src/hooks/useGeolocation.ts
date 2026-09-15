import { useEffect, useState } from 'react';

const DEFAULT_LOCATION: [number, number] = [20.2961, 85.8245];
const LOCATION_STORAGE_KEY = 'sahaayak.shared-location';

function readStoredLocation(): [number, number] | null {
  try {
    const value = JSON.parse(localStorage.getItem(LOCATION_STORAGE_KEY) || 'null');
    return Array.isArray(value) && value.length === 2 ? [Number(value[0]), Number(value[1])] : null;
  } catch {
    return null;
  }
}

function publishLocation(value: [number, number] | null) {
  if (value) localStorage.setItem(LOCATION_STORAGE_KEY, JSON.stringify(value));
  else localStorage.removeItem(LOCATION_STORAGE_KEY);
  window.dispatchEvent(new CustomEvent('sahaayak-location-change', { detail: value }));
}

export function useGeolocation(initial: [number, number] | null = null) {
  const [coordinates, setCoordinatesState] = useState<[number, number] | null>(() => initial ?? readStoredLocation() ?? DEFAULT_LOCATION);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState('');

  const setCoordinates = (value: [number, number] | null) => {
    setCoordinatesState(value);
    publishLocation(value);
  };

  useEffect(() => {
    if (initial) {
      setCoordinates(initial);
    }
  }, [initial]);

  useEffect(() => {
    const syncLocation = (event: Event) => {
      const value = (event as CustomEvent<[number, number] | null>).detail;
      setCoordinatesState(value);
    };
    const syncStorage = () => setCoordinatesState(readStoredLocation() ?? DEFAULT_LOCATION);
    window.addEventListener('sahaayak-location-change', syncLocation);
    window.addEventListener('storage', syncStorage);
    return () => {
      window.removeEventListener('sahaayak-location-change', syncLocation);
      window.removeEventListener('storage', syncStorage);
    };
  }, []);

  const locate = () => {
    setError('');
    if (!navigator.geolocation) {
      setCoordinates(DEFAULT_LOCATION);
      setError('Location is not supported in this browser. Showing Bhubaneswar, Odisha.');
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (result) => {
        setCoordinates([result.coords.latitude, result.coords.longitude]);
        setLocating(false);
      },
      (failure) => {
        setCoordinates(DEFAULT_LOCATION);
        setLocating(false);
        setError(
          failure.code === 1
            ? 'Location permission denied. Showing Bhubaneswar, Odisha.'
            : failure.code === 3
              ? 'Location request timed out. Showing Bhubaneswar, Odisha.'
              : 'Location is unavailable. Showing Bhubaneswar, Odisha.'
        );
      },
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 60000 }
    );
  };

  return { coordinates, setCoordinates, locating, error, locate };
}