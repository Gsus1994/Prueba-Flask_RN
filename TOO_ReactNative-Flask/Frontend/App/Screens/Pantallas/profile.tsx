// Frontend/App/Screens/Pantallas/profile.tsx

import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    Image,
    TouchableOpacity,
    Alert,
    StyleSheet,
} from 'react-native';
import Modal from '../ScreensComponents/modal';
import Loader from '../ScreensComponents/loader';

import { ProfileData } from '../../Types/userTypes';
import { LinearGradient } from 'expo-linear-gradient';
import { TabScreenProps } from '../../Types/navigationTypes';
import { SafeAreaView } from 'react-native-safe-area-context';

import { getProfile, refreshProfile } from '../../Services/userServices';
import { takePhoto, choosePhoto, updateProfileImage } from '../../Services/imageServices';

type Props = TabScreenProps<'Perfil'>;

const ProfileScreen: React.FC<Props> = ({ navigation }) => {
    const [profileData, setProfileData] = useState<{
        firstName: string;
        lastName: string;
        dni: string;
        birthDate: string;
        email: string;
        profileImage: string | null;
    }>({
        firstName: '',
        lastName: '',
        dni: '',
        birthDate: '',
        email: '',
        profileImage: null,
    });
    const [loading, setLoading] = useState(true);
    const [imageReloadAttempted, setImageReloadAttempted] = useState(false);
    const [isModalVisible, setIsModalVisible] = useState<boolean>(false); // Estado para controlar la visibilidad del Modal

    /**
     * Función para obtener los datos del perfil del usuario.
     */
    const fetchProfileData = async () => {
        const MINIMUM_LOADING_TIME = 1000;
        const startTime = Date.now();

        try {
            const data: ProfileData = await getProfile();

            setProfileData({
                firstName: data.nombre,
                lastName: data.apellido,
                dni: data.dni,
                birthDate: data.fecha_nacimiento,
                email: data.email,
                profileImage: data.profile_image_url,
            });
        } catch (error: any) {
            Alert.alert('Error', error.message);
        } finally {
            const elapsedTime = Date.now() - startTime;
            const remainingTime = MINIMUM_LOADING_TIME - elapsedTime;
            if (remainingTime > 0) {
                setTimeout(() => setLoading(false), remainingTime);
            } else {
                setLoading(false);
            }
        }
    };

    /**
     * Función para actualizar la imagen de perfil.
     * @param uri URI de la nueva imagen.
     */
    const handleUpdateProfileImage = async (uri: string) => {
        setLoading(true);
        try {
            const newProfileImageUrl = await updateProfileImage(uri);
            setProfileData((prevState) => ({
                ...prevState,
                profileImage: newProfileImageUrl,
            }));
            Alert.alert('Éxito', 'Imagen de perfil actualizada correctamente.');
        } catch (error: any) {
            Alert.alert('Error', error.message);
        } finally {
            setLoading(false);
        }
    };

    /**
     * Función para manejar la selección de imagen (tomar foto o elegir de la galería).
     * Utiliza las funciones del servicio imagesServices.tsx
     */
    const handleTakePhoto = async () => {
        setIsModalVisible(false);
        const uri = await takePhoto();
        if (uri) {
            await handleUpdateProfileImage(uri);
        }
    };

    const handlePickFromGallery = async () => {
        setIsModalVisible(false);
        const uri = await choosePhoto();
        if (uri) {
            await handleUpdateProfileImage(uri);
        }
    };

    /**
     * Función para manejar la generación de QR (en desarrollo).
     */
    const handleGenerateQR = () => {
        Alert.alert('Función Generar QR', 'Esta función está en desarrollo.');
    };

    /**
     * Función para manejar el escaneo de QR (en desarrollo).
     */
    const handleScanQR = () => {
        Alert.alert('Función Escanear QR', 'Esta función está en desarrollo.');
    };

    useEffect(() => {
        fetchProfileData();
    }, []);

    useEffect(() => {
        if (imageReloadAttempted) {
            setImageReloadAttempted(false);
        }
    }, [profileData.profileImage]);

    return (
        <LinearGradient
            colors={['#ffffff', '#d2f1e6']}
            style={styles.safeArea}
            start={{ x: 0.5, y: 0 }}
            end={{ x: 1, y: 0.5 }}
        >
            <SafeAreaView style={styles.safeArea}>
                <View style={styles.container}>
                    <Text style={styles.title}>Perfil</Text>

                    <TouchableOpacity onPress={() => setIsModalVisible(true)} style={styles.imageContainer}>
                        {profileData.profileImage ? (
                            <Image
                                source={{ uri: profileData.profileImage }}
                                style={styles.profileImage}
                                onError={async (e) => {
                                    console.error('Error cargando la imagen:', e.nativeEvent.error);

                                    if (!imageReloadAttempted) {
                                        setImageReloadAttempted(true);
                                        try {
                                            const refreshedData = await refreshProfile();
                                            setProfileData({
                                                ...profileData,
                                                profileImage: refreshedData.profile_image_url,
                                            });
                                        } catch (error: any) {
                                            Alert.alert('Error', error.message);
                                        }
                                    }
                                }}
                            />
                        ) : (
                            <Image
                                source={require('../../Assets/Images/profile.jpg')}
                                style={styles.profileImage}
                                onError={(e) =>
                                    console.error(
                                        'Error cargando la imagen por defecto:',
                                        e.nativeEvent.error
                                    )
                                }
                            />
                        )}
                    </TouchableOpacity>

                    {/* Modal */}
                    <Modal
                        visible={isModalVisible}
                        onClose={() => setIsModalVisible(false)}
                        onTakePhoto={handleTakePhoto}
                        onPickFromGallery={handlePickFromGallery}
                    />

                    <View style={styles.shadowContainer}>
                        <View style={styles.labelContainer}>
                            <Text style={styles.labelTitle}>Nombre:</Text>
                            <Text style={styles.label}>{profileData.firstName}</Text>
                        </View>

                        <View style={styles.labelContainer}>
                            <Text style={styles.labelTitle}>Apellidos:</Text>
                            <Text style={styles.label}>{profileData.lastName}</Text>
                        </View>

                        <View style={styles.labelContainer}>
                            <Text style={styles.labelTitle}>DNI:</Text>
                            <Text style={styles.label}>{profileData.dni}</Text>
                        </View>

                        <View style={styles.labelContainer}>
                            <Text style={styles.labelTitle}>Fecha de Nacimiento:</Text>
                            <Text style={styles.label}>{profileData.birthDate}</Text>
                        </View>

                        <View style={styles.labelContainer}>
                            <Text style={styles.labelTitle}>Correo Electrónico:</Text>
                            <Text style={styles.label}>{profileData.email}</Text>
                        </View>
                    </View>

                    <View style={styles.buttonContainer}>
                        <TouchableOpacity style={styles.button} onPress={handleGenerateQR}>
                            <Text style={styles.buttonText}>Generar QR</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={styles.button} onPress={handleScanQR}>
                            <Text style={styles.buttonText}>Escanear QR</Text>
                        </TouchableOpacity>
                    </View>
                </View>
                {/* Agrega el Loader */}
                <Loader visible={loading} message="Procesando..." />
            </SafeAreaView>
        </LinearGradient>
    );

};
export default ProfileScreen;

const styles = StyleSheet.create({
    safeArea: {
        flex: 1,
    },
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        marginBottom: 40,
        alignSelf: 'flex-start',
    },
    imageContainer: {
        marginBottom: 20,
        position: 'relative',
    },
    profileImage: {
        width: 150,
        height: 150,
        borderRadius: 75,
        borderColor: '#000',
        borderWidth: 5,
        resizeMode: 'cover',
        marginBottom: 20,
    },
    shadowContainer: {
        width: '100%',
        padding: 15,
        borderRadius: 10,
        backgroundColor: '#fff',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.9,
        shadowRadius: 2,
        elevation: 5,
        marginBottom: 20,
    },
    labelContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 15,
        width: '100%',
    },
    labelTitle: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    label: {
        fontSize: 16,
        color: '#333',
        textAlign: 'right',
    },
    buttonContainer: {
        marginTop: 20,
        width: '100%',
        justifyContent: 'space-between',
    },
    button: {
        backgroundColor: '#4CAF50',
        padding: 15,
        borderRadius: 10,
        marginVertical: 10,
        width: '100%',
        alignItems: 'center',
    },
    buttonText: {
        color: '#fff',
        fontSize: 16,
    },
    loaderContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    loadingText: {
        marginTop: 10,
        fontSize: 16,
        color: '#000',
    },
});