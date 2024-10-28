// Frontend/App/Services/userServices.tsx

import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { ProfileData } from '../Types/userTypes';

const API_URL = 'http://192.168.1.45:6969';

/**
 * Type guard para verificar si el error es de Axios con una respuesta.
 * @param error Error a verificar.
 */
export function isAxiosErrorWithResponse(
    error: any
): error is { response: { status: number; data: any } } {
    return (
        error &&
        typeof error === 'object' &&
        'response' in error &&
        error.response &&
        'status' in error.response &&
        'data' in error.response
    );
}

/**
 * Obtiene los datos del perfil del usuario.
 * @returns Datos del perfil del usuario.
 */
export const getProfile = async (): Promise<ProfileData> => {
    try {
        const token = await AsyncStorage.getItem('access_token');
        if (!token) {
            throw new Error('No se encontró el token de autenticación.');
        }

        const response = await axios.get<ProfileData>(`${API_URL}/profile`, {
            headers: { Authorization: `Bearer ${token}` },
            timeout: 5000,
        });

        if (response.status === 200) {
            return response.data;
        } else {
            throw new Error('No se pudieron obtener los datos del perfil.');
        }
    } catch (error: any) {
        if (isAxiosErrorWithResponse(error)) {
            if (error.response.status === 401) {
                throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
            }
            throw new Error(error.response.data.msg || 'Error al obtener los datos del perfil.');
        } else if (error instanceof Error) {
            throw new Error(error.message);
        } else {
            throw new Error('Ocurrió un error desconocido al obtener el perfil.');
        }
    }
};

/**
 * Refresca los datos del perfil del usuario.
 * @returns Datos actualizados del perfil.
 */
export const refreshProfile = async (): Promise<ProfileData> => {
    // Funciona igual que getProfile, añadir lógica adicional si es necesario
    return await getProfile();
};