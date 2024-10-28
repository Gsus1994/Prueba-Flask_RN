// Frontend/App/Services/imageServices.tsx

import { Alert } from 'react-native';
import { Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { isAxiosErrorWithResponse } from './userServices';

const API_URL = 'http://192.168.1.45:6969';

/**
 * Solicita permisos para acceder a la cámara.
 * @returns Booleano indicando si los permisos fueron otorgados.
 */
export const requestCameraPermission = async (): Promise<boolean> => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
        Alert.alert(
            'Permiso de Cámara Denegado',
            'Necesitas otorgar permisos para usar la cámara.'
        );
        return false;
    }
    return true;
};

/**
 * Solicita permisos para acceder a la galería de imágenes.
 * @returns Booleano indicando si los permisos fueron otorgados.
 */
export const requestMediaLibraryPermission = async (): Promise<boolean> => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
        Alert.alert(
            'Permiso de Galería Denegado',
            'Necesitas otorgar permisos para acceder a la galería.'
        );
        return false;
    }
    return true;
};

/**
 * Abre la cámara para tomar una foto.
 * @returns URI de la imagen tomada o null si fue cancelado.
 */
export const takePhoto = async (): Promise<string | null> => {
    const hasPermission = await requestCameraPermission();
    if (!hasPermission) return null;

    const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 4],
        quality: 1,
    });

    if (!result.canceled && result.assets.length > 0) {
        return result.assets[0].uri;
    }

    return null;
};

/**
 * Abre la galería para seleccionar una imagen.
 * @returns URI de la imagen seleccionada o null si fue cancelado.
 */
export const choosePhoto = async (): Promise<string | null> => {
    const hasPermission = await requestMediaLibraryPermission();
    if (!hasPermission) return null;

    const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 4],
        quality: 1,
    });

    if (!result.canceled && result.assets.length > 0) {
        return result.assets[0].uri;
    }

    return null;
};


/**
 * Actualiza la imagen de perfil del usuario.
 * @param uri URI de la nueva imagen de perfil.
 * @returns Nueva URL de la imagen de perfil.
 */
export const updateProfileImage = async (uri: string): Promise<string> => {
    try {
        const token = await AsyncStorage.getItem('access_token');
        if (!token) {
            throw new Error('No se encontró el token de autenticación.');
        }

        const formData = new FormData();
        const filename = uri.split('/').pop() || 'profile.jpg';
        const match = /\.(\w+)$/.exec(filename);
        const type = match ? `image/${match[1]}` : `image`;

        formData.append('profile_image', {
            uri: Platform.OS === 'android' ? uri : uri.replace('file://', ''),
            name: filename,
            type,
        } as any);

        const response = await axios.put<{ profile_image_url: string }>(`${API_URL}/profile/image`, formData, {
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'multipart/form-data',
            },
            timeout: 5000,
        });

        if (response.status === 200) {
            return response.data.profile_image_url;
        } else {
            throw new Error('No se pudo actualizar la imagen de perfil.');
        }
    } catch (error: any) {
        if (isAxiosErrorWithResponse(error)) {
            if (error.response.status === 401) {
                throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
            }
            throw new Error(error.response.data.msg || 'Error al actualizar la imagen de perfil.');
        } else if (error instanceof Error) {
            throw new Error(error.message);
        } else {
            throw new Error('Ocurrió un error desconocido al actualizar la imagen de perfil.');
        }
    }
};