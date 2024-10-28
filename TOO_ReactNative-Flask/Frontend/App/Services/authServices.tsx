// Frontend/App/Services/authServices.tsx

import axios from 'axios';
import { LoginData, LoginResponse, SignupData, SignupResponse } from '../Types/formTypes';

const API_URL = 'http://192.168.1.45:6969';

export const loginUser = async (userData: LoginData): Promise<LoginResponse> => {
    try {
        const response = await axios.post<LoginResponse>(`${API_URL}/login`, userData, {
            headers: { 'Content-Type': 'application/json' },
            timeout: 5000,
        });
        return response.data;
    } catch (error: any) {
        if (error.response) {
            throw new Error(error.response.data.msg || 'Error en el proceso de login');
        } else {
            throw new Error('Error de conexión');
        }
    }
};

export const requestPasswordReset = async (email: string) => {
    try {
        const response = await axios.post(`${API_URL}/password-reset/request`, { email });
        return response.data;
    } catch (error: any) {
        if (error.response) {
            throw new Error(error.response.data.msg || 'Error al solicitar restablecimiento de contraseña');
        } else {
            throw new Error('Error de conexión');
        }
    }
};

export const confirmPasswordReset = async (email: string, code: string, new_password: string) => {
    try {
        const response = await axios.post(`${API_URL}/password-reset/confirm`, { email, code, new_password });
        return response.data;
    } catch (error: any) {
        if (error.response) {
            throw new Error(error.response.data.msg || 'Error al confirmar restablecimiento de contraseña');
        } else {
            throw new Error('Error de conexión');
        }
    }
};

/**
 * Función para registrar un nuevo usuario.
 * @param userData Datos del usuario para el registro.
 * @returns Respuesta del servidor.
 */
export const signupUser = async (userData: SignupData): Promise<SignupResponse> => {
    try {
        const formData = new FormData();
        formData.append('nombre', userData.nombre);
        formData.append('apellidos', userData.apellidos);
        formData.append('dni', userData.dni);
        formData.append('fecha_nacimiento', userData.fecha_nacimiento);
        formData.append('email', userData.email);
        formData.append('password', userData.password);
        formData.append('profile_image', {
            uri: userData.profile_image.uri,
            name: userData.profile_image.name,
            type: userData.profile_image.type,
        } as any);

        const response = await axios.post<SignupResponse>(`${API_URL}/register`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            timeout: 10000,
        });

        return response.data;
    } catch (error: any) {
        if (error.response) {
            throw new Error(error.response.data.msg || 'Error en el proceso de registro');
        } else {
            throw new Error('Error de conexión');
        }
    }
};