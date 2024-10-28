// Frontend/App/Screens/Auth/recovery.tsx

import React, { useState } from 'react';
import {
    View,
    Text,
    Alert,
    StyleSheet,
    KeyboardTypeOptions,
    Button,
} from 'react-native';
import Loader from '../ScreensComponents/loader';
import CustomInput from './AuthComponents/customInput';

import { LinearGradient } from 'expo-linear-gradient';
import { useForm } from 'react-hook-form';
import { StackScreenProps } from '@react-navigation/stack';
import { SafeAreaView } from 'react-native-safe-area-context';

import { RootStackParamList } from '../../Types/navigationTypes';
import { RecoveryFormData } from '../../Types/formTypes';
import { requestPasswordReset, confirmPasswordReset } from '../../Services/authServices';

type Props = StackScreenProps<RootStackParamList, 'Recovery'>;

const RecoveryScreen: React.FC<Props> = ({ navigation }) => {
    const { control, handleSubmit, formState: { errors }, watch } = useForm<RecoveryFormData>();

    const [step, setStep] = useState<'email' | 'code' | 'new_password'>('email');
    const [email, setEmail] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);

    // Funciones para cada paso del proceso de recuperación

    // Enviar código al email
    const onSubmitEmail = async (data: RecoveryFormData) => {
        setLoading(true);
        try {
            await requestPasswordReset(data.email);
            setEmail(data.email);
            setStep('code');
            Alert.alert('Éxito', 'Se ha enviado un correo con el código de restablecimiento.');
        } catch (error: any) {
            Alert.alert('Error', error.message);
        } finally {
            setLoading(false);
        }
    };

    // Verificar código
    const onSubmitCode = async (data: RecoveryFormData) => {
        setLoading(true);
        try {
            // verificar el código en el backend
            setStep('new_password');
        } catch (error: any) {
            Alert.alert('Error', error.message);
        } finally {
            setLoading(false);
        }
    };

    // Restablecer contraseña
    const onSubmitPassword = async (data: RecoveryFormData) => {
        if (data.new_password !== data.confirm_password) {
            Alert.alert('Error', 'Las contraseñas no coinciden.');
            return;
        }

        setLoading(true);
        try {
            await confirmPasswordReset(email, data.code || '', data.new_password || '');
            Alert.alert('Éxito', 'Tu contraseña ha sido actualizada correctamente.');
            navigation.navigate('Login');
        } catch (error: any) {
            Alert.alert('Error', error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <LinearGradient
            colors={['#ffffff', '#909090']}
            style={styles.container}
            start={{ x: 0.5, y: 0 }}
            end={{ x: 1, y: 1 }}
        >
            <SafeAreaView style={styles.safeArea}>
                <View style={styles.contentContainer}>
                    <Text style={styles.title}>Restablecer Contraseña</Text>

                    {/* Mostrar Loader */}
                    <Loader visible={loading} message="Procesando..." />

                    {!loading && step === 'email' && (
                        <View style={styles.formContainer}>
                            <CustomInput
                                control={control}
                                name="email"
                                placeholder="Correo Electrónico"
                                iconName="envelope"
                                keyboardType="email-address"
                                rules={{
                                    required: 'El email es obligatorio',
                                    pattern: {
                                        value: /^\S+@\S+\.\S+$/,
                                        message: 'Ingresa un email válido',
                                    },
                                }}
                            />

                            <Button
                                title="Enviar Código"
                                onPress={handleSubmit(onSubmitEmail)}
                            />
                        </View>
                    )}

                    {!loading && step === 'code' && (
                        <View style={styles.formContainer}>
                            <Text style={styles.subtitle}>Ingresa el código de 6 dígitos enviado a tu email</Text>
                            <CustomInput
                                control={control}
                                name="code"
                                placeholder="Código"
                                iconName="key"
                                keyboardType="number-pad"
                                maxLength={6}
                                rules={{
                                    required: 'El código es obligatorio',
                                    pattern: {
                                        value: /^\d{6}$/,
                                        message: 'El código debe tener 6 dígitos',
                                    },
                                }}
                            />

                            <Button
                                title="Verificar Código"
                                onPress={handleSubmit(onSubmitCode)}
                            />
                        </View>
                    )}

                    {!loading && step === 'new_password' && (
                        <View style={styles.formContainer}>
                            <CustomInput
                                control={control}
                                name="new_password"
                                placeholder="Nueva Contraseña"
                                iconName="lock"
                                secureTextEntry
                                rules={{
                                    required: 'La nueva contraseña es obligatoria',
                                    minLength: {
                                        value: 8,
                                        message: 'La contraseña debe tener al menos 8 caracteres',
                                    },
                                    pattern: {
                                        value: /^(?=.*[A-Z])(?=.*\d).+$/,
                                        message: 'La contraseña debe tener al menos una mayúscula y un número',
                                    },
                                }}
                            />
                            <CustomInput
                                control={control}
                                name="confirm_password"
                                placeholder="Confirmar Nueva Contraseña"
                                iconName="lock"
                                secureTextEntry
                                rules={{
                                    required: 'Confirmar contraseña es obligatorio',
                                    validate: (value: KeyboardTypeOptions | undefined) =>
                                        value === watch('new_password') || 'Las contraseñas no coinciden',
                                }}
                            />

                            <Button
                                title="Restablecer Contraseña"
                                onPress={handleSubmit(onSubmitPassword)}
                            />
                        </View>
                    )}
                </View>
            </SafeAreaView>
        </LinearGradient>
    );

};

export default RecoveryScreen;

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    safeArea: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    contentContainer: {
        width: '100%',
        maxWidth: 400,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 20,
        textAlign: 'center',
        color: '#333',
    },
    subtitle: {
        fontSize: 16,
        marginBottom: 10,
        textAlign: 'center',
        color: '#333',
    },
    formContainer: {
        marginTop: 25,
    },
});