import { useState, useRef } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { User, Upload, X, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ProfileSettingsProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

const ProfileSettings = ({ open, onOpenChange }: ProfileSettingsProps) => {
    const { user, updateProfile, logout } = useAuth();
    const [name, setName] = useState(user?.name || '');
    const [profilePhoto, setProfilePhoto] = useState(user?.profilePhoto || '');
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const navigate = useNavigate();

    const handleFileSelect = (file: File) => {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const result = e.target?.result as string;
                setProfilePhoto(result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files[0];
        handleFileSelect(file);
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            handleFileSelect(file);
        }
    };

    const handleSave = () => {
        if (name.trim()) {
            updateProfile(name, profilePhoto);
            onOpenChange(false);
        }
    };

    const handleLogout = () => {
        logout();
        onOpenChange(false);
        navigate('/auth');
    };

    const handleRemovePhoto = () => {
        setProfilePhoto('');
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle className="font-orbitron">Profile Settings</DialogTitle>
                    <DialogDescription className="font-electrolize">
                        Manage your profile information and settings
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-6 py-4">
                    {/* Profile Photo */}
                    <div className="space-y-3">
                        <Label className="font-electrolize">Profile Photo</Label>
                        <div className="flex items-center gap-4">
                            <div className="relative">
                                {profilePhoto ? (
                                    <div className="relative w-20 h-20 rounded-full overflow-hidden ring-2 ring-primary/50">
                                        <img
                                            src={profilePhoto}
                                            alt="Profile"
                                            className="w-full h-full object-cover"
                                        />
                                        <button
                                            onClick={handleRemovePhoto}
                                            className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-destructive flex items-center justify-center hover:bg-destructive/80 transition-colors"
                                        >
                                            <X className="w-3 h-3 text-white" />
                                        </button>
                                    </div>
                                ) : (
                                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary via-secondary to-accent flex items-center justify-center">
                                        <User className="w-10 h-10 text-white" />
                                    </div>
                                )}
                            </div>

                            <div
                                onDrop={handleDrop}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                className={`flex-1 border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-all ${isDragging
                                        ? 'border-primary bg-primary/10'
                                        : 'border-muted-foreground/30 hover:border-primary/50'
                                    }`}
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <Upload className="w-6 h-6 mx-auto mb-2 text-muted-foreground" />
                                <p className="text-sm text-muted-foreground font-electrolize">
                                    {isDragging ? 'Drop image here' : 'Click or drag image to upload'}
                                </p>
                                <p className="text-xs text-muted-foreground/70 mt-1 font-electrolize">
                                    PNG, JPG up to 5MB
                                </p>
                            </div>

                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                onChange={handleFileInput}
                                className="hidden"
                            />
                        </div>
                    </div>

                    {/* Name */}
                    <div className="space-y-2">
                        <Label htmlFor="profile-name" className="font-electrolize">Name</Label>
                        <Input
                            id="profile-name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="Enter your name"
                            className="glass bg-background/30"
                        />
                    </div>

                    {/* Email (read-only) */}
                    <div className="space-y-2">
                        <Label htmlFor="profile-email" className="font-electrolize">Email</Label>
                        <Input
                            id="profile-email"
                            value={user?.email || ''}
                            disabled
                            className="glass bg-muted/30 cursor-not-allowed"
                        />
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 pt-4">
                        <Button
                            onClick={handleSave}
                            className="flex-1 bg-gradient-to-r from-primary via-secondary to-accent font-orbitron"
                        >
                            Save Changes
                        </Button>
                        <Button
                            onClick={handleLogout}
                            variant="destructive"
                            className="flex items-center gap-2 font-orbitron"
                        >
                            <LogOut className="w-4 h-4" />
                            Logout
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default ProfileSettings;
