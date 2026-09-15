import { get, set } from 'idb-keyval';
import { createAdvisory, uploadFile } from '../api/advisories';
import { Submission } from '../types';
export interface Queued { id: string; owner: string; payload: Submission; files: File[]; created_at: string; error?: string }
export const readQueue = async (): Promise<Queued[]> => (await get('sahaayak-queue')) || [];
export async function queueSubmission(item: Queued) { const queue = await readQueue(); if (!queue.some(q => q.id === item.id)) await set('sahaayak-queue', [...queue, item]); window.dispatchEvent(new Event('queue-change')); }
export async function removeQueued(id: string) { await set('sahaayak-queue', (await readQueue()).filter(q => q.id !== id)); window.dispatchEvent(new Event('queue-change')); }
let syncing = false;
export async function syncQueue(owner: string) {
 if (syncing) return 0; syncing = true; let count = 0;
 try { for (const item of await readQueue()) {
   if (item.owner !== owner) continue;
   try { const uploads = await Promise.all(item.files.map(uploadFile)); await createAdvisory({...item.payload, upload_ids: [...item.payload.upload_ids, ...uploads.map(u => u.id)]}); await removeQueued(item.id); count++; }
   catch (e: any) { const current = await readQueue(); await set('sahaayak-queue', current.map(q => q.id === item.id ? {...q, error: e.message} : q)); break; }
 } } finally {syncing = false; window.dispatchEvent(new Event('queue-change'));}
 if(count) {
   const detail={owner,count,time:new Date().toISOString()};
   localStorage.setItem(`sahaayak-last-sync:${owner}`,JSON.stringify(detail));
   window.dispatchEvent(new CustomEvent('queue-synced',{detail}));
 }
 return count;
}
export async function compressImage(file: File): Promise<File> {
 if (!file.type.startsWith('image/') || file.size < 300000) return file;
 const image = await createImageBitmap(file); const ratio = Math.min(1, 1400 / Math.max(image.width, image.height));
 const canvas = document.createElement('canvas'); canvas.width = Math.round(image.width * ratio); canvas.height = Math.round(image.height * ratio);
 canvas.getContext('2d')!.drawImage(image, 0, 0, canvas.width, canvas.height); image.close();
 const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, 'image/jpeg', .75));
 if (!blob) return file; return blob.size < file.size ? new File([blob], file.name.replace(/\.[^.]+$/, '.jpg'), {type: 'image/jpeg'}) : file;
}