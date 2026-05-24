import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { createGreenhouseSocket, greenhouseApi, REALTIME_ENABLED } from '../services/api';

const GreenhouseContext = createContext(null);

export function GreenhouseProvider({ children }) {
  const [sensors, setSensors] = useState({});
  const [history, setHistory] = useState([]);
  const [status, setStatus] = useState({});
  const [autoMode, setAutoMode] = useState(true);
  const [devices, setDevices] = useState({
    drip_pump: false,
    rain_pump: false,
    photo_led: false,
    insect_led: false,
    cooler_1: false,
    cooler_2: false,
  });
  const [thresholds, setThresholds] = useState({
    temperature: 30,
    moisture: 40,
    light: 420,
  });

  const refresh = useCallback(async () => {
    try {
      const [sensorData, historyData, statusData] = await Promise.all([
        greenhouseApi.getSensors(),
        greenhouseApi.getHistory(),
        greenhouseApi.getStatus(),
      ]);
      setSensors((current) => ({ ...current, ...sensorData }));
      setHistory(Array.isArray(historyData) ? historyData : []);
      setStatus(statusData);
      if (statusData?.devices) {
        setDevices((current) => ({ ...current, ...statusData.devices }));
      }
    } catch (error) {
      console.error('Data refresh error:', error);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!REALTIME_ENABLED) return undefined;

    const socket = createGreenhouseSocket();

    const handleSensorUpdate = (sensorData) => {
      setSensors((current) => ({ ...current, ...sensorData }));
    };

    const handleHistoryInit = (historyData) => {
      if (Array.isArray(historyData) && historyData.length > 0) {
        setHistory(historyData);
      }
    };

    const handleHistoryAppend = (point) => {
      if (!point) return;
      setHistory((current) => [...current, point].slice(-96));
    };

    const handleDeviceUpdate = (snapshot) => {
      if (snapshot?.devices) {
        setDevices((current) => ({ ...current, ...snapshot.devices }));
      }
      setStatus((current) => ({ ...current, ...snapshot, websocket: 'ulangan' }));
    };

    const handleStatusUpdate = (statusData) => {
      setStatus((current) => ({ ...current, ...statusData, websocket: 'ulangan' }));
    };

    socket.on('connect', () => {
      setStatus((current) => ({ ...current, websocket: 'ulangan' }));
    });
    socket.on('disconnect', () => {
      setStatus((current) => ({ ...current, websocket: 'uzilgan' }));
    });
    socket.on('connect_error', () => {
      setStatus((current) => ({ ...current, websocket: 'auth xato' }));
    });
    socket.on('sensor:update', handleSensorUpdate);
    socket.on('history:init', handleHistoryInit);
    socket.on('history:append', handleHistoryAppend);
    socket.on('device:update', handleDeviceUpdate);
    socket.on('status:update', handleStatusUpdate);
    socket.connect();

    return () => {
      socket.disconnect();
    };
  }, []);

  // Frontend automation disabled - control only via site buttons
  // Backend PI_AUTOMATION_ENABLED controls auto mode if needed

  const setDevice = async (device, enabled) => {
    setDevices((current) => ({ ...current, [device]: enabled }));
    try {
      const response = await greenhouseApi.setDevice(device, enabled, 'site');
      if (response.data?.devices) {
        setDevices((current) => ({ ...current, ...response.data.devices }));
      }
    } catch (error) {
      console.info(`${device} qurilmasi lokal navbatga qo'yildi:`, error.message);
    }
  };

  const value = useMemo(
    () => ({
      sensors,
      history,
      status,
      alerts: status.alerts || [],
      activityLogs: status.logs || [],
      gpioPins: status.gpio || [],
      devices,
      autoMode,
      thresholds,
      refresh,
      setDevice,
      setAutoMode,
      setThresholds,
    }),
    [autoMode, devices, history, refresh, sensors, status, thresholds],
  );

  return <GreenhouseContext.Provider value={value}>{children}</GreenhouseContext.Provider>;
}

export function useGreenhouse() {
  const value = useContext(GreenhouseContext);
  if (!value) {
    throw new Error('useGreenhouse GreenhouseProvider ichida ishlatilishi kerak');
  }
  return value;
}
