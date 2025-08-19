import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5005/api';

/** Data Payload for translation
* @param {object} payload - The translation payload.
* @param {string} payload.text - The text to translate.
* @param {string} payload.src_lang - The source language code.
* @param {string} payload.tgt_lang - The target language code.
* @returns {Promise} An axios promise.
*/
export const translateText = (payload) => {
    return axios.post(`${API_BASE_URL}/translate`, payload);
};