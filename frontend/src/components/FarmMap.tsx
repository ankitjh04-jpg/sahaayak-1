import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { api } from '../api/client';
import { FarmField } from '../types';
import { GoogleFarmMap } from './GoogleFarmMap';
import { useGeolocation } from '../hooks/useGeolocation';
interface Props {fields?: FarmField[]; onSelect?: (lat:number,lng:number)=>void; selected?: [number,number] | null}
const EMPTY_FIELDS:FarmField[]=[];
export const FarmMap = ({fields=EMPTY_FIELDS,onSelect,selected}: Props) => {
 const sharedLocation = useGeolocation();
 const mapSelected = selected === undefined ? sharedLocation.coordinates : selected;
 const mapOnSelect = onSelect || ((lat:number,lng:number)=>sharedLocation.setCoordinates([lat,lng]));
 const [config,setConfig]=useState<any>(null),[failed,setFailed]=useState(false);
 useEffect(()=>{api('/config').then(setConfig).catch(()=>setConfig({}));},[]);
 if(config?.google_maps_browser_key&&!failed)return <GoogleFarmMap apiKey={config.google_maps_browser_key} mapId={config.google_maps_map_id} fields={fields} onSelect={mapOnSelect} selected={mapSelected} onFailure={()=>setFailed(true)}/>;
 return <div><LeafletFarmMap fields={fields} onSelect={mapOnSelect} selected={mapSelected}/><p className="map-provider-note" data-testid="map-provider-status">{failed?'Google Maps unavailable. Showing OpenStreetMap.':'OpenStreetMap · Google Maps activates when its browser key is configured.'}</p></div>;
};
const LeafletFarmMap = ({fields=EMPTY_FIELDS,onSelect,selected}: Props) => {
 const ref=useRef<HTMLDivElement>(null); const mapRef=useRef<L.Map|null>(null); const layerRef=useRef<L.LayerGroup|null>(null); const callback=useRef(onSelect);callback.current=onSelect;
 const [error,setError]=useState('');
 useEffect(()=>{ if(!ref.current)return;
   // Map tiles intentionally extend beyond their canvas while panning. A shadow
   // canvas isolates their positioning and styles from the page layout.
   const shadow=ref.current.shadowRoot||ref.current.attachShadow({mode:'open'});
   const css=document.createElement('link');css.rel='stylesheet';css.href='/leaflet.css';
   const container=document.createElement('div');container.style.cssText='height:100%;width:100%;position:relative;overflow:hidden;font-family:inherit';container.setAttribute('data-testid','leaflet-map-canvas');
   shadow.replaceChildren(css,container);
   const map=L.map(container,{scrollWheelZoom:false}).setView([20.59,78.96],5);mapRef.current=map;layerRef.current=L.layerGroup().addTo(map);
   api('/config').then(c=>{const layer=L.tileLayer(c.map_tile_url,{attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',maxZoom:19});layer.on('tileerror',()=>setError('Map tiles unavailable. Your field details are still saved.'));layer.on('tileload',()=>setError(''));layer.addTo(map);}).catch(()=>setError('Map unavailable while offline.'));
   map.on('click',(e:L.LeafletMouseEvent)=>callback.current?.(Number(e.latlng.lat.toFixed(6)),Number(e.latlng.lng.toFixed(6)))); const resize=new ResizeObserver(()=>map.invalidateSize());resize.observe(ref.current);
   return()=>{resize.disconnect();map.remove();mapRef.current=null;};
 },[]);
 useEffect(()=>{const group=layerRef.current,map=mapRef.current;if(!group||!map)return;group.clearLayers();const points:[number,number][]=[];
  fields.forEach(f=>{if(f.latitude==null||f.longitude==null)return;const point:[number,number]=[f.latitude,f.longitude];points.push(point);const label=document.createElement('div');label.textContent=`${f.name} · ${f.crop} · ${f.acreage} acres`;L.circleMarker(point,{radius:9,color:'#fff',weight:3,fillColor:'#28533e',fillOpacity:1}).bindPopup(label).addTo(group);});
  if(selected){points.push(selected);L.circleMarker(selected,{radius:9,color:'#fff',weight:3,fillColor:'#b99846',fillOpacity:1}).addTo(group);}
  if(points.length)map.fitBounds(L.latLngBounds(points),{padding:[35,35],maxZoom:14});
 },[fields,selected]);
 return <div className="farm-map-wrap"><div className="farm-map" ref={ref} data-testid="farm-map"/>{error&&<div className="map-error" data-testid="map-error">{error}</div>}</div>;
};