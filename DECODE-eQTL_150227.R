# Detect eQTL by dynamic slicing.
# Songpeng Zu
# 2015-02-27

# Gene Expression Data by Zhirui Hu.

#-- load the libraries
library(Rcpp) # used for DECODE
library(dynslicing) # used for DECODE
library(data.table) # used for loading big data
library(stringr) # used for getSampleIds

#-- Supplementary Data Directory 
supdir <- "/n/home00/szu/KR_eQTL/GTex"

#-- Get the input parameters
args <- commandArgs(trailingOnly = TRUE)
# The start/end point is only dependent on genelocsnp data.
# They should be the same across different tissues.
gene_residual <- fread(args[1],skip=1) # Read gene residuals' matrix, full path needed.
startpoint <- strtoi(args[2]) # gene lable start 
endpoint <- strtoi(args[3]) # gene lable end
tissuenm <- args[4]

#--Define outputfile name
outdir <- "/n/home00/szu/gtex"
outfilename <- paste(paste(outdir,tissuenm,sep="/"),startpoint,endpoint,sep="_")

#-- Get the genes' name, samples' name and gene_residual_matrix
con <- file(args[1],open="r")
templine < - readLines(con,n=1)
close(con)
gene_samplenm <- strsplit(templine,split="\t")
#gene_samplenm <- colnames(gene_residual)[2:ncol(gene_residual)]
genenm <- unlist(gene_residual[,1,with=FALSE])
gene_residual_matrix <- as.matrix(gene_residual[1:nrow(gene_residual),2:ncol(gene_residual),with=FALSE])
dimnames(gene_residual_matrix) <- list(genenm,gene_samplenm)
rm(gene_residual)

# FUNCTION of extracting SNP samples' names from gene_samplenm.
getSNPsampleIds <- function(genenmstr){
    txt <- gsub("\\.","-",genenmstr)
    m = str_match_all(txt,'(^G.*)-[0-9]{4}')
    return(m[[1]][2])
}
gene2snp_samplenm <- unlist(apply(as.matrix(gene_samplenm),1,function(x) getSNPsampleIds(x)))
colnames(gene_residual_matrix) <- gene2snp_samplenm
# Evarage gene residuals by the same colnames (i.e., the same samples)
if (anyDuplicated(gene2snp_samplenm)){
    gene_residual_matrix <- sapply(unique(gene2snp_samplenm),function(i) rowMeans(gene_residual_matrix[,gene2snp_samplenm]))
}

#-- Get the snps' name, samples' name and snp_value_matrix
snp_samplenm <- as.matrix(read.table(paste(supdir,"GTEx.SNP.sampleID",sep="/"))) 
snp_value <- fread(paste(supdir,"GTEx.wholegenome.SNP",sep="/"))
snp_value_matrix <- as.matrix(snp_value[ ,2:ncol(snp_value),with=FALSE])
dimnames(snp_value_matrix) <- list(snp_value$V1, snp_samplenm[ ,1])
mode(snp_value_matrix) <- "numeric" # Convert the character matrix to numeric.
rm(snp_value)

#-- Reorganize both of the matrix based on the samples' ID.
cosamplenm <- intersect(gene2snp_samplenm,colnames(snp_value_matrix))

gene_re_matrix <- gene_residual_matrix[ ,cosamplenm]
rm(gene_residual_matrix)

snp_tmp_matrix <- snp_value_matrix[ ,cosamplenm]
# Filter SNPs whose MAF <5% or >95%
snp_sumrow <- rowSums(snp_tmp_matrix,na.rm=TRUE)
snp_nanum <- rowSums(is.na(snp_tmp_matrix))
snp_rowsamplenum <- 2*(ncol(snp_tmp_matrix) - snp_nanum) # SNP are recorded as 0,1,2
snp_rowsamplenum[which(snp_rowsamplenum==0)] <- 1 # Avoid 0.
snp_rowratio <- snp_sumrow/snp_rowsamplenum
# We might ignore the situation that most samples' values of a given SNP are 1. 
snp_need <- row.names(snp_tmp_matrix)[which(snp_rowratio>=0.05 & snp_rowratio <= 0.95)]
snp_re_matrix <- snp_tmp_matrix[snp_need,]
rm(snp_value_matrix)

#-- Load rownames (genes' names) in the genelocsnp
genenm_loc <- as.matrix(read.table(paste(supdir,"loc_gene_ensemble",sep="/"),
                                   header=FALSE,quote="", colClasses = "character"))
# Load gene-snp relationship information
gene2snptotal <- as.matrix(fread(paste(supdir,"genelocsnp",sep="/"),header=FALSE,sep="\n"))
row.names(gene2snptotal) <- genenm_loc

#-- FUNCTION of DECODE 
eqtlDECODE <- function(genestartnm,geneendnm){
    # Get the final genes with genelocsnp and gene residual information.
    genearray <- as.matrix(intersect(genenm_loc[genestartnm:geneendnm,],genenm))
    gene2snpsub <- as.matrix(gene2snptotal[genearray,])
        
    getgene2snp <- function(gene2snpstr){
        myVector <- strsplit(gene2snpstr,"\t")
        return(intersect(snp_need,myVector[[1]][2:length(myVector[[1]] )])) 
    }
    
    gene2snp <- apply(gene2snpsub,1,function(x) getgene2snp(x))
    rm(gene2snptotal,gene2snpsub)

    # FUNCTION Of DECODE for single gene.
    eqtlDECODEsingle <- function(singlenm){
        # The singlenm should be in the gene_residual_matrix.
        genearray <- gene_re_matrix[singlenm, ]
        # The singlenm should also be in the gene2snp.
        snparray <- snp_re_matrix[unlist(gene2snp[[singlenm]]), ]
        snparray_order <- snparray[ ,order(genearray)]
        rm(snparray)
        # Set the parameters.
        dim <- 3 # The categories of SNPs.(0,1,2)
        lambda <- 1.0
        alpha <- 1.0
        decode_values <- apply(snparray_order,1,function(x) ds_bf_u(x[!is.na(x)],dim,lambda,alpha))
        cat(paste(c(singlenm,decode_values),collapse="\t"),file=outfilename,sep="\n",append=TRUE)
    }
    # apply the eqtlDECODEsingle function.
    apply(genearray,1,function(x) eqtlDECODEsingle(x))
}

#-- Main Function
eqtlDECODE(genestartnm,geneendnm)

#-- Note: after getting the results, 
# the script of "Out_DECODE_Result.py" 
# is used to extract the final format of the DECODE results.




