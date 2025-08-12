import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

/*The data to be sent, containing text, src_lang, and tgt_lang.*/
export const translateText = (payload) => {
    return axios.post(`${API_BASE_URL}/translate`, payload);
};
