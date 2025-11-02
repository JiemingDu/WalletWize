import React from "react";

export type BrandHeaderProps = {
  product: string;
  subtitle?: string;
  logoSrc?: string;
};

const BrandHeader: React.FC<BrandHeaderProps> = ({
  product,
  subtitle,
  logoSrc,
}) => {
  return (
    <header className="mx-auto max-w-6xl px-6 pt-8 pb-2">
      {/* logo + title */}
      <div className="mx-auto flex items-center justify-center gap-6 sm:gap-8">
        {logoSrc ? (
          <img
            src={logoSrc}
            alt={`${product} logo`}
            className="h-28 sm:h-32 md:h-36 w-auto" // keep logo size
            draggable={false}
          />
        ) : null}

        <div className="text-center sm:text-left">
          {/* BIG header text in Jersey 10 */}
          <h1 className="font-jersey leading-none text-5xl sm:text-6xl md:text-7xl">
            {product}
          </h1>
          {subtitle && (
            <p className="mt-2 text-slate-600 font-jersey text-lg sm:text-xl">
              {subtitle}
            </p>
          )}
        </div>
      </div>
      {/* Divider removed */}
    </header>
  );
};

export default BrandHeader;