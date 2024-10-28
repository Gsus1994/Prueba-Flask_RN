// Frontend/App/Screens/Auth/signup.tsx

import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    Button,
    Image,
    TouchableOpacity,
    Alert,
    StyleSheet,
} from 'react-native';
import Modal from '../ScreensComponents/modal';
import Loader from '../ScreensComponents/loader';
import Icon from 'react-native-vector-icons/FontAwesome';
import DateTimePicker from '@react-native-community/datetimepicker';
import { useForm, Controller } from 'react-hook-form';
import { LinearGradient } from 'expo-linear-gradient';
import { StackScreenProps } from '@react-navigation/stack';
import { SafeAreaView } from 'react-native-safe-area-context';

import { signupUser } from '../../Services/authServices';
import { RootStackParamList } from '../../Types/navigationTypes';
import { takePhoto, choosePhoto } from '../../Services/imageServices';
import { SignupData, SignupFormInputs, SignupResponse } from '../../Types/formTypes';

type Props = StackScreenProps<RootStackParamList, 'Signup'>;

const SignupScreen: React.FC<Props> = ({ navigation }) => {
    const {
        control,
        handleSubmit,
        formState: { errors, isSubmitted },
        watch,
        setError,
        clearErrors,
    } = useForm<SignupFormInputs>();

    const [profileImage, setProfileImage] = useState<string | null>(null);
    const [date, setDate] = useState<Date | null>(null);
    const [showDatePicker, setShowDatePicker] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [isModalVisible, setIsModalVisible] = useState<boolean>(false);
    const [loading, setLoading] = useState(false);

    const handleUpdateProfileImage = (uri: string) => {
        setProfileImage(uri);
        clearErrors('profileImage');
    };

    const handleTakePhoto = async () => {
        setIsModalVisible(false);
        const uri = await takePhoto();
        if (uri) {
            handleUpdateProfileImage(uri);
        }
    };

    const handlePickFromGallery = async () => {
        setIsModalVisible(false);
        const uri = await choosePhoto();
        if (uri) {
            handleUpdateProfileImage(uri);
        }
    };

    const showDatePickerHandler = () => {
        setShowDatePicker(true);
    };

    const onDateChange = (event: any, selectedDate?: Date) => {
        setShowDatePicker(false);
        if (selectedDate) {
            setDate(selectedDate);
            clearErrors('date');
        }
    };

    const onSubmit = async (data: SignupFormInputs) => {
        clearErrors(['profileImage', 'date']);

        let valid = true;

        // Validar imagen de perfil
        if (!profileImage) {
            setError('profileImage', {
                type: 'manual',
                message: 'Debe seleccionar una imagen de perfil.',
            });
            valid = false;
        }

        // Validar fecha de nacimiento
        if (!date) {
            setError('date', {
                type: 'manual',
                message: 'Debe seleccionar una fecha de nacimiento.',
            });
            valid = false;
        } else {
            const today = new Date();
            const ageDifMs = today.getTime() - date.getTime();
            const ageDate = new Date(ageDifMs);
            const age = Math.abs(ageDate.getUTCFullYear() - 1970);
            if (age < 18) {
                setError('date', {
                    type: 'manual',
                    message: 'Debes ser mayor de 18 años para registrarte.',
                });
                valid = false;
            }
        }

        // Validar contraseñas
        if (data.password !== data.confirmPassword) {
            setError('confirmPassword', {
                type: 'manual',
                message: 'Las contraseñas no coinciden',
            });
            valid = false;
        }

        if (!valid) {
            return;
        }

        setLoading(true);

        try {
            const formData: SignupData = {
                nombre: data.nombre,
                apellidos: data.apellidos,
                dni: data.dni,
                fecha_nacimiento: date!.toISOString().split('T')[0],
                email: data.email,
                password: data.password,
                confirmPassword: data.confirmPassword,
                profile_image: {
                    uri: profileImage!,
                    name: profileImage!.split('/').pop() || 'profile.jpg',
                    type: 'image/jpeg',
                },
            };

            const response: SignupResponse = await signupUser(formData);

            Alert.alert('Éxito', 'Usuario registrado exitosamente');
            navigation.replace('Login');
        } catch (error: any) {
            console.error('Error en el proceso de registro:', error);

            let errorMsg = 'Error en el proceso de registro';

            if (error.message) {
                errorMsg = error.message;
            } else {
                errorMsg = 'No se pudo conectar con el servidor. Verifica tu conexión.';
            }

            Alert.alert('Error', errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <LinearGradient colors={['#ffffff', '#808080']} style={styles.container}>
            <SafeAreaView>
                <Text style={styles.title}>Crea tu cuenta</Text>

                <View style={styles.imageSection}>
                    <TouchableOpacity onPress={() => setIsModalVisible(true)} style={styles.imageContainer}>
                        {profileImage ? (
                            <Image source={{ uri: profileImage }} style={styles.profileImage} />
                        ) : (
                            <Image
                                source={require('../../Assets/Images/select_profile.png')}
                                style={styles.profileImage}
                            />
                        )}
                    </TouchableOpacity>
                    {errors.profileImage?.message && isSubmitted && (
                        <Text style={styles.errorImage}>{errors.profileImage.message}</Text>
                    )}
                </View>

                {/* Modal para seleccionar imagen */}
                <Modal
                    visible={isModalVisible}
                    onClose={() => setIsModalVisible(false)}
                    onTakePhoto={handleTakePhoto}
                    onPickFromGallery={handlePickFromGallery}
                />

                {/* Selector de Fecha de Nacimiento */}
                <TouchableOpacity
                    onPress={showDatePickerHandler}
                    style={styles.inputContainer}
                >
                    <Text style={[styles.text, { color: date ? '#303030' : 'gray' }]}>
                        {date ? date.toLocaleDateString() : 'Fecha de nacimiento'}
                    </Text>
                    <Icon name="calendar" size={20} color="#000" style={styles.icon} />
                </TouchableOpacity>
                {errors.date?.message && isSubmitted && (
                    <Text style={styles.error}>{errors.date.message}</Text>
                )}

                {showDatePicker && (
                    <DateTimePicker
                        value={date || new Date()}
                        mode="date"
                        display="default"
                        onChange={onDateChange}
                        maximumDate={new Date()}
                    />
                )}

                {/* Campo DNI */}
                <Controller
                    control={control}
                    name="dni"
                    rules={{
                        required: 'Este campo es obligatorio',
                        pattern: {
                            value: /^[0-9]{8}[A-Za-z]$/,
                            message: 'El DNI debe tener 8 dígitos y una letra al final',
                        },
                    }}
                    render={({ field: { onChange, onBlur, value } }) => (
                        <TextInput
                            style={styles.input}
                            onBlur={onBlur}
                            onChangeText={onChange}
                            value={value}
                            placeholder="DNI"
                            keyboardType="default"
                            autoCapitalize="characters"
                        />
                    )}
                />
                {errors.dni?.message && isSubmitted && (
                    <Text style={styles.error}>{errors.dni.message}</Text>
                )}

                {/* Campo Nombre */}
                <Controller
                    control={control}
                    name="nombre"
                    rules={{ required: 'Este campo es obligatorio' }}
                    render={({ field: { onChange, onBlur, value } }) => (
                        <TextInput
                            style={styles.input}
                            onBlur={onBlur}
                            onChangeText={onChange}
                            value={value}
                            placeholder="Nombre"
                        />
                    )}
                />
                {errors.nombre?.message && isSubmitted && (
                    <Text style={styles.error}>{errors.nombre.message}</Text>
                )}

                {/* Campo Apellidos */}
                <Controller
                    control={control}
                    name="apellidos"
                    rules={{ required: 'Este campo es obligatorio' }}
                    render={({ field: { onChange, onBlur, value } }) => (
                        <TextInput
                            style={styles.input}
                            onBlur={onBlur}
                            onChangeText={onChange}
                            value={value}
                            placeholder="Apellidos"
                        />
                    )}
                />
                {errors.apellidos?.message && isSubmitted && (
                    <Text style={styles.error}>{errors.apellidos.message}</Text>
                )}

                {/* Campo Email */}
                <Controller
                    control={control}
                    name="email"
                    rules={{
                        required: 'Este campo es obligatorio',
                        pattern: {
                            value: /^\S+@\S+\.\S+$/,
                            message: 'Ingrese un correo válido',
                        },
                    }}
                    render={({ field: { onChange, onBlur, value } }) => (
                        <TextInput
                            style={styles.input}
                            onBlur={onBlur}
                            onChangeText={onChange}
                            value={value}
                            placeholder="Correo Electrónico"
                            keyboardType="email-address"
                            autoCapitalize="none"
                        />
                    )}
                />
                {errors.email?.message && isSubmitted && (
                    <Text style={styles.error}>{errors.email.message}</Text>
                )}

                {/* Campo Contraseña */}
                <Controller
                    control={control}
                    name="password"
                    rules={{
                        required: 'Este campo es obligatorio',
                        minLength: {
                            value: 8,
                            message: 'La contraseña debe tener al menos 8 caracteres',
                        },
                        validate: (value) => {
                            const hasUpperCase = /[A-Z]/.test(value);
                            const hasLowerCase = /[a-z]/.test(value);

                            if (!hasUpperCase) {
                                return 'La contraseña debe contener al menos una letra mayúscula';
                            }
                            if (!hasLowerCase) {
                                return 'La contraseña debe contener al menos una letra minúscula';
                            }
                            return true;
                        },
                    }}
                    render={({ field: { onChange, onBlur, value } }) => (
                        <View style={styles.inputContainer}>
                            <TextInput
                                style={[styles.inputWithoutBorder, styles.text]}
                                onBlur={onBlur}
                                onChangeText={onChange}
                                value={value}
                                placeholder="Contraseña"
                                secureTextEntry={!showPassword}
                            />
                            <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                                <Icon
                                    name={showPassword ? 'eye-slash' : 'eye'}
                                    size={20}
                                    color="#000"
                                />
                            </TouchableOpacity>
                        </View>
                    )}
                />
                {errors.password?.message && isSubmitted && (
                    <Text style={styles.error}>{errors.password.message}</Text>
                )}

                {/* Campo Confirmar Contraseña */}
                <Controller
                    control={control}
                    name="confirmPassword"
                    rules={{
                        required: 'Confirmar contraseña es obligatorio',
                        validate: (value) => {
                            if (value !== watch('password')) {
                                return 'Las contraseñas no coinciden';
                            }
                            return true;
                        },
                    }}
                    render={({ field: { onChange, onBlur, value } }) => (
                        <View style={styles.inputContainer}>
                            <TextInput
                                style={[styles.inputWithoutBorder, styles.text]}
                                onBlur={onBlur}
                                onChangeText={onChange}
                                value={value}
                                placeholder="Repetir Contraseña"
                                secureTextEntry={!showConfirmPassword}
                            />
                            <TouchableOpacity onPress={() => setShowConfirmPassword(!showConfirmPassword)}>
                                <Icon
                                    name={showConfirmPassword ? 'eye-slash' : 'eye'}
                                    size={20}
                                    color="#000"
                                />
                            </TouchableOpacity>
                        </View>
                    )}
                />
                {errors.confirmPassword?.message && isSubmitted && (
                    <Text style={styles.error}>{errors.confirmPassword.message}</Text>
                )}

                <View style={styles.buttonContainer}>
                    <Button title="Registrar" onPress={handleSubmit(onSubmit)} />
                </View>
            </SafeAreaView>
            <Loader visible={loading} message="Registrando usuario..." />
        </LinearGradient>
    );
};
export default SignupScreen;

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        padding: 20,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 30,
        textAlign: 'center',
    },
    text: {
        fontSize: 14,
        paddingHorizontal: 9,
        color: '#303030',
    },
    input: {
        height: 40,
        borderBottomWidth: 1,
        borderColor: 'gray',
        marginBottom: 12,
        paddingHorizontal: 10,
        backgroundColor: 'transparent',
        width: '100%',
        color: '#303030',
    },
    inputWithoutBorder: {
        flex: 1,
        paddingHorizontal: 10,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 12,
        borderBottomWidth: 1,
        borderColor: 'gray',
        width: '100%',
    },
    icon: {
        paddingHorizontal: 10,
        paddingVertical: 7,
    },
    error: {
        color: 'red',
        marginBottom: 10,
    },
    errorImage: {
        color: 'red',
        marginTop: 5,
        textAlign: 'center',
    },
    imageSection: {
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 20,
    },
    imageContainer: {
        justifyContent: 'center',
        alignItems: 'center',
    },
    profileImage: {
        width: 100,
        height: 100,
        borderRadius: 50,
        marginBottom: 10,
    },
    buttonContainer: { marginTop: 20 },
});