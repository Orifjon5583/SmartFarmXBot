import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { activityLogs, alerts, gpioPins, historySeries, sensorSnapshot } from '../assets/greenhouseData';
import { greenhouseApi } from '../services/api';
import { deriveAutomationState } from '../utils/automation';

const GreenhouseContext = createContext(null);

export function GreenhouseProvider({ children }) {
  const [sensors, setSensors] = useState(sensorSnapshot);
  const [history, setHistory] = useState(historySeries);
  const [status, setStatus] = useState({});
  const [autoMode, setAutoMode] = useState(true);
  const [devices, setDevices] = useState({
    fan: true,
    pump: false,
    light: true,
    camera: true,
  });
  const [thresholds, setThresholds] = useState({
    temperature: 30,
    moisture: 40,
    light: 420,
  });

  const refresh = useCallback(async () => {
    const [sensorData, historyData, statusData] = await Promise.all([
      greenhouseApi.getSensors(),
      greenhouseApi.getHistory(),
      greenhouseApi.getStatus(),
    ]);
    setSensors((current) => ({ ...current, ...sensorData }));
    setHistory(Array.isArray(historyData) ? historyData : historySeries);
    setStatus(statusData);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!autoMode) return;
    setDevices((current) => ({
      ...current,
      ...deriveAutomationState(sensors, thresholds),
    }));
  }, [autoMode, sensors, thresholds]);

  const setDevice = async (device, enabled) => {
    setDevices((current) => ({ ...current, [device]: enabled }));
    try {
      await greenhouseApi.setDevice(device, enabled);
    } catch (error) {
      console.info(`${device} qurilmasi lokal navbatga qo‘yildi:`, error.message);
    }
  };

  const value = useMemo(
    () => ({
      sensors,
      history,
      status,
      alerts,
      activityLogs,
      gpioPins,
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
