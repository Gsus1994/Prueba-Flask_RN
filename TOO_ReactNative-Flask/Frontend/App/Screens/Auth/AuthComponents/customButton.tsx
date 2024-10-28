// Frontend/App/Screens/Auth/AuthComponents/customButton.tsx

import React from 'react';
import { TouchableOpacity, Text, StyleSheet, TouchableOpacityProps } from 'react-native';
import { COLORS } from '../../../Constants/colors';

interface CustomButtonProps extends TouchableOpacityProps {
    title: string;
    backgroundColor?: string;
    textColor?: string;
}

const CustomButton: React.FC<CustomButtonProps> = ({
    onPress,
    title,
    backgroundColor = COLORS.buttonColor,
    textColor = COLORS.buttonText,
    style,
    ...rest
}) => (
    <TouchableOpacity
        style={[styles.button, { backgroundColor }, style]}
        onPress={onPress}
        {...rest}
    >
        <Text style={[styles.buttonText, { color: textColor }]}>{title}</Text>
    </TouchableOpacity>
);

export default CustomButton;

const styles = StyleSheet.create({
    button: {
        padding: 15,
        borderRadius: 15,
        alignItems: 'center',
        marginTop: 25,
    },
    buttonText: {
        fontSize: 14,
        fontWeight: 'bold',
    },
});