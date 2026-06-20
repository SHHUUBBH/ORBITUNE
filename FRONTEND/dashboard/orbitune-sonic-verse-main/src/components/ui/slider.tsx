import * as React from "react";
import * as SliderPrimitive from "@radix-ui/react-slider";

import { cn } from "@/lib/utils";

const Slider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SliderPrimitive.Root>
>(({ className, ...props }, ref) => (
  <SliderPrimitive.Root
    ref={ref}
    className={cn("relative flex w-full touch-none select-none items-center group", className)}
    {...props}
  >
    <SliderPrimitive.Track className="relative h-2 w-full grow overflow-hidden rounded-full bg-white/10 backdrop-blur-sm">
      <SliderPrimitive.Range 
        className="absolute h-full rounded-full"
        style={{
          background: 'linear-gradient(to right, rgb(139, 92, 246), rgb(236, 72, 153), rgb(251, 146, 60))',
          boxShadow: '0 0 10px rgba(139, 92, 246, 0.5)',
        }}
      />
    </SliderPrimitive.Track>
    <SliderPrimitive.Thumb 
      className="block h-5 w-5 rounded-full border-2 border-white bg-gradient-to-r from-primary to-secondary ring-offset-background transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:scale-110 active:scale-95 cursor-grab active:cursor-grabbing"
      style={{
        boxShadow: '0 0 15px rgba(139, 92, 246, 0.8), 0 0 5px rgba(236, 72, 153, 0.6)',
      }}
    />
  </SliderPrimitive.Root>
));
Slider.displayName = SliderPrimitive.Root.displayName;

export { Slider };
