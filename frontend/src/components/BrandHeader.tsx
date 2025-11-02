import React from "react";

export type BrandHeaderProps = {
  product: string;
  subtitle?: string;
  logoSrc?: string;
  showDivider?: boolean;
};

const BrandHeader: React.FC<BrandHeaderProps> = ({
  product,
  subtitle,
  logoSrc,
  showDivider = false,
}) => {

return (
  <header className="mx-auto max-w-6xl px-6 pt-10 pb-4">
    {/* logo | title */}
    <div className="mx-auto flex items-center justify-center gap-6 sm:gap-8">
      {/* KEEP LOGO SIZE THE SAME */}
      {logoSrc ? (
        <img
          src={logoSrc}
          alt={`${product} logo`}
          className="h-28 sm:h-32 md:h-36 w-auto"  // logo size
          draggable={false}
        />
      ) : null}

      {/* MAKE ONLY THE TEXT BIGGER */}
      <div className="text-center sm:text-left">
        <h1 className="font-jersey leading-none tracking-tight text-6xl sm:text-7xl lg:text-8xl">
          {product}
        </h1>
        {subtitle ? (
          <p className="mt-2 text-xl sm:text-2xl lg:text-3xl font-medium text-slate-500">
            {subtitle}
          </p>
        ) : null}
      </div>
    </div>

    {/* divider */}
    <div className="mt-6 h-px w-full bg-slate-200" />
  </header>
);
};

export default BrandHeader;