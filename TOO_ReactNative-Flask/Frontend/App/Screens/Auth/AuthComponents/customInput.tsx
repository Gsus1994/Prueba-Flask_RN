// Frontend/App/Screens/Auth/AuthComponents/customInput.tsx

import React from 'react';
import { View, TextInput, StyleSheet, Text, KeyboardTypeOptions } from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';
import { Control, Controller, FieldValues, Path } from 'react-hook-form';
import { COLORS } from '../../../Constants/colors';

interface CustomInputProps<T extends FieldValues> {
    control: Control<T>;
    name: Path<T>;
    rules?: any;
    placeholder: string;
    iconName: string;
    secureTextEntry?: boolean;
    keyboardType?: KeyboardTypeOptions;
    maxLength?: number;
}

const CustomInput = <T extends FieldValues>({
    control,
    name,
    rules,
    placeholder,
    iconName,
    secureTextEntry = false,
    keyboardType = 'default',
    maxLength,
}: CustomInputProps<T>) => (
    <Controller
        control={control}
        name={name}
        rules={rules}
        render={({ field: { onChange, onBlur, value }, fieldState: { error } }) => (
            <>
                <View style={styles.inputContainer}>
                    <Icon name={iconName} size={20} color={COLORS.icon} style={styles.icon} />
                    <TextInput
                        style={styles.input}
                        placeholder={placeholder}
                        onBlur={onBlur}
                        onChangeText={onChange}
                        value={value}
                        secureTextEntry={secureTextEntry}
                        keyboardType={keyboardType}
                        autoCapitalize="none"
                        maxLength={maxLength}
                        accessibilityLabel={placeholder}
                    />
                </View>
                {error && <Text style={styles.errorText}>{error.message}</Text>}
            </>
        )}
    />
);

export default CustomInput;

const styles = StyleSheet.create({
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        borderBottomWidth: 1,
        borderColor: '#000',
        marginBottom: 15,
        paddingVertical: 5,
    },
    icon: {
        marginRight: 10,
    },
    input: {
        flex: 1,
        height: 40,
        fontSize: 16,
        color: COLORS.text,
    },
    errorText: {
        color: COLORS.error,
        marginBottom: 10,
        marginLeft: 5,
    },
});