library(terra)
for(n in c('grid','geolocation')) {
 r<-rast(paste0('outputs/',n,'_dem_0p5m.tif'))
 # Gaussian display smoothing: sigma 1 m, truncated at 2 m; preserve original NoData.
 xy<-expand.grid(-4:4,-4:4); w<-matrix(exp(-((xy[,1]*.5)^2+(xy[,2]*.5)^2)/2),9,9); w<-w/sum(w)
 # Normalized convolution avoids bias at gaps; original coverage is reinstated.
 numerator<-focal(ifel(is.na(r),0,r),w=w,fun='sum',na.rm=TRUE)
 denominator<-focal(ifel(is.na(r),0,1),w=w,fun='sum',na.rm=TRUE)
 smooth<-mask(numerator/denominator,r)
 names(smooth)<-'smoothed_elevation_m_display_only'
 writeRaster(smooth,paste0('outputs/',n,'_dem_smooth_0p5m.tif'),overwrite=TRUE,gdal=c('COMPRESS=DEFLATE','TILED=YES'),datatype='FLT4S')
 hs<-shade(terrain(smooth,'slope',unit='radians'),terrain(smooth,'aspect',unit='radians'),angle=45,direction=c(225,270,315,360));hs<-mean(hs)
 writeRaster(hs,paste0('outputs/',n,'_hillshade_smooth.tif'),overwrite=TRUE,gdal=c('COMPRESS=DEFLATE','TILED=YES'),datatype='FLT4S')
 cat(n,'complete\n')
}
